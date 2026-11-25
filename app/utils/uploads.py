from pathlib import Path
from urllib.parse import unquote, urlsplit

from app.config import UPLOAD_DIR


# Files picked in the file manager are served by the app under this prefix
UPLOAD_PREFIX = "/upload/"


def local_file(url: str) -> Path | None:
    """File in UPLOAD_DIR behind a /upload/... URL, None if not local."""
    path = unquote(urlsplit(url).path)
    if not path.startswith(UPLOAD_PREFIX):
        return None
    root = UPLOAD_DIR.resolve()
    file = (root / path.removeprefix(UPLOAD_PREFIX)).resolve()
    if not file.is_relative_to(root) or not file.is_file():
        return None
    return file
