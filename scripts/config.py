from pathlib import Path
import logging
import sys
from utils.logger import get_logger
from utils.setup_folder import setup_folder
import warnings

warnings.filterwarnings("ignore")

logger = get_logger(__name__, "config")


def main() -> None:
    logger.info("[Config] Config project folders")
    setup_folder()
    logger.info("[Config] Config project folders is complete")


if __name__ == "__main__":
    main()
