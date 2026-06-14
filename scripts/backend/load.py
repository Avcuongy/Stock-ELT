from pathlib import Path
import sys
import logging
from backend.load import load_db_others, load_db_exchanges, load_db_companies
from utils.logger import get_logger
import warnings

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = PROJECT_ROOT / "logs" / "backend.log"

logger = get_logger(__name__, "backend")


def main() -> None:
    logger.info("[Backend - Load] Start")
    load_db_others()
    load_db_exchanges()
    load_db_companies()
    logger.info("[Backend - Load] Finished")


if __name__ == "__main__":
    main()
