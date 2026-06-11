from pathlib import Path
import os
import sys
import json
import datetime
import traceback
import logging
import pandas as pd
from utils.logger import get_logger

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_COMPLETE_DIR = DATA_DIR / "completed"

logger = get_logger(__name__, "elt")


def _get_latest_file_in_directory(directory, extension):
    Path(directory).mkdir(parents=True, exist_ok=True)

    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(extension)
    ]
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file


def _export_to_parquet():
    latest_file = _get_latest_file_in_directory(DATA_RAW_DIR / "ohlcs", ".json")
    if not latest_file:
        logger.warning("[Load] Warning: No raw OHLC file found.")
        return None

    with open(latest_file, "r", encoding="utf-8") as f:
        ohlc_data = json.load(f)

    processed_ohlcs = []
    for record in ohlc_data:
        processed_record = {
            "ticker": record.get("ticker", record.get("T")),
            "open": record.get("open", record.get("o")),
            "high": record.get("high", record.get("h")),
            "low": record.get("low", record.get("l")),
            "close": record.get("close", record.get("c")),
            "volume": record.get("volume", record.get("v")),
            "vwap": record.get("vwap", record.get("vw")),
            "timestamp": record.get("timestamp", record.get("t")),
            "transactions": record.get("transactions", record.get("n")),
            "otc": record.get("otc", False),
        }
        processed_ohlcs.append(processed_record)

    df = pd.DataFrame(processed_ohlcs)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    type_mapping = {
        "ticker": "string",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "float64",
        "vwap": "float64",
        "transactions": "Int64",
        "otc": "boolean",
    }

    for col, dtype in type_mapping.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype)

    timestamp_str = datetime.datetime.now().strftime("%Y_%m_%d")
    output_dir = DATA_COMPLETE_DIR / "ohlcs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"ohlcs_{timestamp_str}.parquet"

    df.to_parquet(output_file, engine="pyarrow", compression="snappy", index=False)

    logger.info(f"[Load] Converted {len(df)} OHLC records to Parquet at: {output_file}")

    return output_file


def convert_api_to_parquet():
    try:
        _export_to_parquet()

    except Exception as e:
        logger.error(f"[Load] Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    convert_api_to_parquet()
