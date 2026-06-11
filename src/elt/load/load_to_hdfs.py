import os
import sys
import logging
from pathlib import Path
from hdfs import InsecureClient
import warnings

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOGS_DIR = PROJECT_ROOT / "logs" / "elt.log"
DATA_DIR = PROJECT_ROOT / "data"
WEBHDFS_URL = "http://localhost:9870"
HDFS_USER = "root"
HDFS_BASE_DIR = "/data_lake"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def _get_hdfs_client() -> InsecureClient:
    url = WEBHDFS_URL
    user = HDFS_USER

    return InsecureClient(url, user=user)


def _upload_parquet_folders(
    client: InsecureClient, local_completed_dir: Path, hdfs_base_dir: str
) -> None:
    """Upload local Parquet files under data/completed to HDFS via WebHDFS."""

    mapping = {
        "db": "db",
        "ohlcs": "ohlcs",
    }

    hdfs_base_dir = hdfs_base_dir.rstrip("/") or "/"

    for local_sub, hdfs_sub in mapping.items():
        local_path = local_completed_dir / local_sub
        hdfs_target = (
            f"{hdfs_base_dir}/{hdfs_sub}" if hdfs_base_dir != "/" else f"/{hdfs_sub}"
        )

        if not local_path.is_dir():
            logger.info(f"[Load] Local directory not found: {local_path}")
            continue

        parquet_files = sorted(local_path.glob("*.parquet"))
        if not parquet_files:
            logger.info(f"[Load] No Parquet files in: {local_path}")
            continue

        client.makedirs(hdfs_target)

        for file_path in parquet_files:
            dest_path = f"{hdfs_target}/{file_path.name}"
            logger.info(f"[Load] Putting {file_path.name} to {dest_path}")

            client.upload(dest_path, str(file_path), overwrite=True)


def load_to_hdfs() -> None:
    local_completed_dir = DATA_DIR / "completed"

    hdfs_base_dir = HDFS_BASE_DIR

    logger.info("[Load] Loading Parquet files into HDFS (WebHDFS)")
    logger.info("[Load] Local completed : %s", local_completed_dir)
    logger.info("[Load] HDFS base dir   : %s", hdfs_base_dir)
    logger.info("[Load] WEBHDFS url     : %s", os.getenv("WEBHDFS_URL", WEBHDFS_URL))

    client = _get_hdfs_client()

    _upload_parquet_folders(client, local_completed_dir, hdfs_base_dir)

    logger.info("[Load] HDFS load completed (WebHDFS).")


if __name__ == "__main__":
    load_to_hdfs()
