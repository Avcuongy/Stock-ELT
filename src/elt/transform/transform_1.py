from pathlib import Path
import os
import sys
import logging
import traceback
import pandas as pd
import duckdb
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import warnings

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOGS_DIR = PROJECT_ROOT / "logs" / "elt.log"
DATA_DIR = PROJECT_ROOT / "data"
DUCKDB_PATH = PROJECT_ROOT / "data_warehouse.duckdb"
HDFS_RPC_URL = "hdfs://localhost:9000"
HDFS_BASE_DIR = "/data_lake"
HDFS_DB_DIR = f"{HDFS_RPC_URL}{HDFS_BASE_DIR}/db"
HDFS_OHLCS_DIR = f"{HDFS_RPC_URL}{HDFS_BASE_DIR}/ohlcs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def _get_spark_session():
    return (
        SparkSession.builder.appName("elt_transform")
        .config("spark.hadoop.dfs.client.use.datanode.hostname", "true")
        .getOrCreate()
    )


def _build_dim_company(spark: SparkSession):
    raw_companies = spark.read.parquet(f"{HDFS_DB_DIR}/companies_*.parquet")
    df_dim_company = raw_companies.select(
        col("company_ticker"),
        col("company_name"),
        col("company_cik"),
        col("company_is_delisted").cast("boolean"),
        col("company_location"),
    ).distinct()
    return df_dim_company


def _build_dim_exchange(spark: SparkSession):
    raw_exchanges = spark.read.parquet(f"{HDFS_DB_DIR}/exchanges_*.parquet")
    raw_regions = spark.read.parquet(f"{HDFS_DB_DIR}/regions_*.parquet")

    df_dim_exchange = (
        raw_exchanges.join(
            raw_regions,
            raw_exchanges.exchange_region_id == raw_regions.region_id,
            "left",
        )
        .select(
            col("exchange_name"),
            col("region_name"),
            col("region_market_type"),
            col("region_local_open"),
            col("region_local_close"),
        )
        .distinct()
    )
    return df_dim_exchange


def _build_dim_industry(spark: SparkSession):
    raw_companies = spark.read.parquet(f"{HDFS_DB_DIR}/companies_*.parquet")
    raw_industries = spark.read.parquet(f"{HDFS_DB_DIR}/industries_*.parquet")
    raw_sic = spark.read.parquet(f"{HDFS_DB_DIR}/sicindustries_*.parquet")

    df_dim_industry = (
        raw_companies.join(
            raw_industries,
            raw_companies.company_industry_id == raw_industries.industry_id,
            "left",
        )
        .join(raw_sic, raw_companies.company_sic_id == raw_sic.sic_id, "left")
        .select(
            col("industry_sector"),
            col("industry_name"),
            col("company_category"),
            col("sic_industry"),
            col("sic_sector"),
        )
        .distinct()
    )
    return df_dim_industry


def transform_1(spark: SparkSession = None):
    should_stop_spark = False
    if spark is None:
        spark = _get_spark_session()
        should_stop_spark = True

    df_dim_company = _build_dim_company(spark)
    df_dim_exchange = _build_dim_exchange(spark)
    df_dim_industry = _build_dim_industry(spark)

    pd_dim_company = df_dim_company.toPandas()
    pd_dim_exchange = df_dim_exchange.toPandas()
    pd_dim_industry = df_dim_industry.toPandas()

    # fix exchange local open/close time format to HH:MM:SS
    for c in ["region_local_open", "region_local_close"]:
        pd_dim_exchange[c] = (
            pd.to_timedelta(pd_dim_exchange[c])
            .astype(str)
            .str.extract(r"(\d{2}:\d{2}:\d{2})")[0]
        )

    logger.info("[Transform] Inserting tables into DuckDB with SCD is_current flag")
    with duckdb.connect(str(DUCKDB_PATH)) as conn:
        conn.execute("SET schema = 'DataWarehouse'")

        conn.execute("""
            INSERT INTO DIM_COMPANY (company_ticker, company_name, company_cik, company_is_delisted, company_location, is_current)
            SELECT company_ticker, company_name, company_cik, company_is_delisted, company_location, TRUE FROM pd_dim_company
        """)

        conn.execute("""
            INSERT INTO DIM_EXCHANGE (exchange_name, region_name, region_market_type, region_local_open, region_local_close, is_current)
            SELECT exchange_name, region_name, region_market_type, region_local_open, region_local_close, TRUE FROM pd_dim_exchange
        """)

        conn.execute("""
            INSERT INTO DIM_INDUSTRY (industry_sector, industry_name, company_category, sic_industry, sic_sector, is_current)
            SELECT industry_sector, industry_name, company_category, sic_industry, sic_sector, TRUE FROM pd_dim_industry
        """)

        company_count = conn.execute("SELECT COUNT(*) FROM DIM_COMPANY").fetchone()[0]
        exchange_count = conn.execute("SELECT COUNT(*) FROM DIM_EXCHANGE").fetchone()[0]
        industry_count = conn.execute("SELECT COUNT(*) FROM DIM_INDUSTRY").fetchone()[0]

    logger.info(f"[Transform] DIM_COMPANY records : {company_count:,}")
    logger.info(f"[Transform] DIM_EXCHANGE records: {exchange_count:,}")
    logger.info(f"[Transform] DIM_INDUSTRY records: {industry_count:,}")
    logger.info(
        "[Transform] Successfully transformed dim_company, dim_exchange, dim_industry and loaded into DuckDB"
    )

    if should_stop_spark:
        spark.stop()


if __name__ == "__main__":
    transform_1()
