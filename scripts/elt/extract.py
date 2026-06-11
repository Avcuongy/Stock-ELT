from pathlib import Path
import sys
import logging
from elt.extract import crawl_ohlcs
import warnings

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = PROJECT_ROOT / "logs" / "elt.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("[Extract] ETL Start")
    crawl_ohlcs()
    logger.info("[Extract] ETL Finished")


if __name__ == "__main__":
    main()
