from pathlib import Path
import logging
import sys
import warnings

from utils.setup_folder import setup_folder

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = PROJECT_ROOT / "logs" / "config.log"


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOGS_DIR, mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.info("[Config] Config project folders")
    setup_folder()
    logging.info("[Config] Config project folders is complete")


if __name__ == "__main__":
    main()
