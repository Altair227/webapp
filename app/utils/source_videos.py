from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from flask import current_app

from app.database import db_session
from app.models import SourceVideo


# Files picked in the file manager are served by the app under this prefix
UPLOAD_PREFIX = "/upload/"


def _local_file(url: str) -> Path | None:
    """File in UPLOAD_DIR behind a /upload/... URL, None if not local."""
    path = unquote(urlsplit(url).path)
    if not path.startswith(UPLOAD_PREFIX):
        return None
    root = Path(current_app.config["UPLOAD_DIR"]).resolve()
    file = (root / path.removeprefix(UPLOAD_PREFIX)).resolve()
    if not file.is_relative_to(root) or not file.is_file():
        return None
    return file


def _describe(video: SourceVideo) -> None:
    name = PurePosixPath(unquote(urlsplit(video.url).path)).name
    suffix = PurePosixPath(name).suffix.lstrip(".").lower()
    video.filename = name[:255] or None
    video.extension = suffix if 0 < len(suffix) <= 5 else None
    file = _local_file(video.url)
    video.size = file.stat().st_size if file else None


def get_or_create_videos(urls: list[str]) -> list[SourceVideo]:
    """SourceVideo rows for the URLs, in the same order.

    Existing rows are reused (url is unique) and undeleted; new ones get
    filename, extension and, for files in UPLOAD_DIR, size. Rows are
    added to the session, the caller commits.
    """
    urls = list(dict.fromkeys(urls))
    if not urls:
        return []
    existing = {
        video.url: video
        for video in db_session.query(SourceVideo).filter(
            SourceVideo.url.in_(urls)
        )
    }
    result = []
    for url in urls:
        video = existing.get(url)
        if video is None:
            video = SourceVideo(url=url)
            _describe(video)
            db_session.add(video)
        video.is_deleted = False
        result.append(video)
    return result
