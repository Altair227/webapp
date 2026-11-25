from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit

from app.database import db_session
from app.models import SourceVideo
from app.utils.uploads import local_file
from app.utils.video_types import detect_type


def _describe(video: SourceVideo) -> None:
    video.type = detect_type(video.url)
    name = PurePosixPath(unquote(urlsplit(video.url).path)).name
    suffix = PurePosixPath(name).suffix.lstrip(".").lower()
    video.filename = name[:255] or None
    video.extension = suffix if 0 < len(suffix) <= 5 else None
    file = local_file(video.url)
    video.size = file.stat().st_size if file else None


def get_or_create_videos(urls: list[str]) -> list[SourceVideo]:
    """SourceVideo rows for the URLs, in the same order.

    Existing rows are reused (url is unique) and undeleted; new ones get
    type, filename, extension and, for files in UPLOAD_DIR, size. Rows are
    added to the session, the caller commits. Posters are found later by
    `cli.py scan-videos`.
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
