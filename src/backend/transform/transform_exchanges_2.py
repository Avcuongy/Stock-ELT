from pathlib import Path
import os
import sys
import json
import datetime
import hashlib
from utils.logger import get_logger

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
LOGS_DIR = PROJECT_ROOT / "logs" / "backend.log"

logger = get_logger(__name__, "backend")


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


def _cleanup_old_files(directory: Path, current_file: Path):
    if not directory.exists():
        return

    for f in directory.glob("*.json"):
        if f.name != current_file.name:
            try:
                f.unlink()
                logger.info(f"[Backend - Transform] Removed old file: {f.name}")
            except Exception as e:
                logger.error(f"[Backend - Transform] Error removing {f.name}: {e}")


def _generate_id(text):
    return hashlib.md5(text.encode()).hexdigest()


def transform_exchanges():
    markets_raw_dir = DATA_RAW_DIR / "markets"
    exchanges_processed_dir = DATA_PROCESSED_DIR / "exchanges"

    latest_file = _get_latest_file_in_directory(markets_raw_dir, ".json")
    if not latest_file:
        logger.info("[Backend - Transform] No raw markets file found.")
        return

    with open(latest_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    exchanges_dict = {}

    for item in raw_data:
        region = item.get("region", "")
        market_type = item.get("market_type", "")
        primary_exchanges = item.get("primary_exchanges", "")
        local_open = item.get("local_open", "")
        local_close = item.get("local_close", "")

        exchange_list = [
            ex.strip() for ex in primary_exchanges.split(",") if ex.strip()
        ]

        for exchange_name in exchange_list:
            key = exchange_name

            if key not in exchanges_dict:
                exchanges_dict[key] = {
                    "id": _generate_id(exchange_name),
                    "name": exchange_name,
                    "region": region,
                    "market_type": market_type,
                    "local_open": local_open,
                    "local_close": local_close,
                }

    exchanges = list(exchanges_dict.values())
    today = datetime.datetime.now().strftime("%Y_%m_%d")

    exchanges_processed_dir.mkdir(parents=True, exist_ok=True)
    output_file = exchanges_processed_dir / f"exchanges_{today}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(exchanges, f, indent=2, ensure_ascii=False)

    logger.info(f"[Backend - Transform] Transformed {len(exchanges)} exchanges.")

    _cleanup_old_files(exchanges_processed_dir, output_file)

    return exchanges


if __name__ == "__main__":
    transform_exchanges()
