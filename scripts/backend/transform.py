from pathlib import Path
import sys
import logging
from backend.transform import transform_others, transform_exchanges, transform_companies
from utils.logger import get_logger
import warnings

warnings.filterwarnings("ignore")

logger = get_logger(__name__, "backend")


def main() -> None:
    logger.info("[Backend - Transform] Start")
    transform_others()
    transform_exchanges()
    transform_companies()
    logger.info("[Backend - Transform] Finished")


if __name__ == "__main__":
    main()
