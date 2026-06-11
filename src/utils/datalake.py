import logging
import os
import sys
from pathlib import Path

from hdfs import InsecureClient

DEFAULT_WEBHDFS_URL = "http://localhost:9870"
DEFAULT_HDFS_USER = "root"

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOGS_DIR = PROJECT_ROOT / "logs" / "elt.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)


class DataLakeClient:
    """Client for interacting with HDFS through WebHDFS."""

    def __init__(
        self,
        webhdfs_url: str | None = None,
        user: str | None = None,
    ) -> None:
        self.webhdfs_url = (
            webhdfs_url or os.getenv("WEBHDFS_URL") or DEFAULT_WEBHDFS_URL
        )

        self.user = user or os.getenv("HDFS_USER") or DEFAULT_HDFS_USER

        try:
            self.client = InsecureClient(
                self.webhdfs_url,
                user=self.user,
            )

            self.client.status("/")

            logging.info(
                "[HDFS] Connected to Data Lake: %s (User: %s)",
                self.webhdfs_url,
                self.user,
            )

        except Exception as exc:
            logging.error(
                "[HDFS] Failed to connect to Data Lake: %s",
                exc,
            )
            raise

    def upload_file(
        self,
        local_path: Path,
        hdfs_path: str,
        overwrite: bool = True,
    ) -> bool:
        """Upload a local file to HDFS."""

        if not local_path.exists():
            logging.error(
                "[HDFS] Local file not found: %s",
                local_path,
            )
            return False

        try:
            self._ensure_hdfs_directory(hdfs_path)

            self.client.upload(
                hdfs_path,
                str(local_path),
                overwrite=overwrite,
            )

            logging.info(
                "[HDFS - Upload] Success: %s -> %s",
                local_path.name,
                hdfs_path,
            )

            return True

        except Exception as exc:
            logging.error(
                "[HDFS - Upload] Failed: %s (%s)",
                local_path.name,
                exc,
            )
            return False

    def download_file(
        self,
        hdfs_path: str,
        local_path: Path,
        overwrite: bool = True,
    ) -> bool:
        """Download a file from HDFS."""

        try:
            local_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.client.download(
                hdfs_path,
                str(local_path),
                overwrite=overwrite,
            )

            logging.info(
                "[HDFS - Download] Success: %s -> %s",
                hdfs_path,
                local_path,
            )

            return True

        except Exception as exc:
            logging.error(
                "[HDFS - Download] Failed: %s (%s)",
                hdfs_path,
                exc,
            )
            return False

    def list_files(self, hdfs_dir: str) -> list[str]:
        """Return all files in an HDFS directory."""

        try:
            files = self.client.list(hdfs_dir)

            logging.info(
                "[HDFS - List] Found %d files in '%s'",
                len(files),
                hdfs_dir,
            )

            return files

        except Exception as exc:
            logging.error(
                "[HDFS - List] Failed to read '%s': %s",
                hdfs_dir,
                exc,
            )
            return []

    def _ensure_hdfs_directory(self, hdfs_path: str) -> None:
        """Create parent directory if it does not exist."""

        parent_dir = Path(hdfs_path).parent.as_posix()

        if parent_dir and parent_dir != ".":
            self.client.makedirs(parent_dir)
