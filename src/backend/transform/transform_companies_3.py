from pathlib import Path
import os
import sys
import json
import datetime
import logging
from utils.logger import get_logger

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"

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


def transform_companies():
    companies_raw_dir = DATA_RAW_DIR / "companies"
    companies_processed_dir = DATA_PROCESSED_DIR / "companies"

    latest_file = _get_latest_file_in_directory(companies_raw_dir, ".json")
    if not latest_file:
        logger.info("[Backend - Transform] No raw companies file found.")
        return

    with open(latest_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    companies = []
    for item in raw_data:
        company = {
            "id": item.get("id"),
            "name": item.get("name"),
            "ticker": item.get("ticker"),
            "cik": item.get("cik"),
            "cusip": item.get("cusip"),
            "exchange": item.get("exchange"),
            "isDelisted": item.get("isDelisted"),
            "category": item.get("category"),
            "sector": item.get("sector"),
            "industry": item.get("industry"),
            "sic": item.get("sic"),
            "currency": item.get("currency"),
            "location": item.get("location"),
        }
        companies.append(company)

    today = datetime.datetime.now().strftime("%Y_%m_%d")

    companies_processed_dir.mkdir(parents=True, exist_ok=True)
    output_file = companies_processed_dir / f"companies_{today}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    logger.info(
        f"[Backend - Transform] Transformed {len(companies)} companies at {output_file}"
    )

    _cleanup_old_files(companies_processed_dir, output_file)

    return companies


if __name__ == "__main__":
    transform_companies()
