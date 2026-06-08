from pathlib import Path
import logging

import warnings

from backend.extract import crawl_markets, crawl_companies

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = PROJECT_ROOT / "logs"


def main() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        filemode="a",
        filename=LOGS_DIR / "Backend.log",
    )
    logging.info("Extract data")
    crawl_markets()
    crawl_companies()
    logging.info("Extract data finished")


if __name__ == "__main__":
    main()
