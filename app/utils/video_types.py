import re
from urllib.parse import parse_qs, urlparse

from app.common.types import VideoType


def extract_youtube_id(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url.strip())
    host = (
        (parsed.hostname or "").lower().removeprefix("www.").removeprefix("m.")
    )
    path = parsed.path.strip("/")
    video_id = None
    if host == "youtu.be":
        video_id = path.split("/")[0]
    elif host in ["youtube.com", "music.youtube.com", "youtube-nocookie.com"]:
        if path == "watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        else:
            parts = path.split("/")
            if len(parts) >= 2 and parts[0] in [
                "embed",
                "shorts",
                "live",
                "v",
            ]:
                video_id = parts[1]
    if video_id and re.compile(r"^[A-Za-z0-9_-]{11}$").match(video_id):
        return video_id
    return None


def extract_vimeo_id(url: str | None) -> tuple[str, str | None] | None:
    """(id, hash) of a Vimeo video; hash is set for unlisted videos only.

    vimeo.com/1, vimeo.com/1/hash, vimeo.com/channels/x/1,
    vimeo.com/groups/x/videos/1, player.vimeo.com/video/1?h=hash
    """
    if not url:
        return None
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower().removeprefix("www.")
    path = parsed.path.strip("/")
    if host == "player.vimeo.com":
        match = re.fullmatch(r"video/(\d+)", path)
    elif host == "vimeo.com":
        match = re.fullmatch(
            r"(?:channels/[^/]+/|groups/[^/]+/videos/)?(\d+)"
            r"(?:/([0-9a-zA-Z]+))?",
            path,
        )
    else:
        return None
    if not match:
        return None
    video_hash = match.group(2) if match.re.groups > 1 else None
    if not video_hash:
        video_hash = parse_qs(parsed.query).get("h", [None])[0]
    if video_hash and not re.fullmatch(r"[0-9a-zA-Z]+", video_hash):
        video_hash = None
    return match.group(1), video_hash


def detect_type(url: str) -> VideoType:
    """Type by the URL alone, no network."""
    try:
        if extract_youtube_id(url):
            return VideoType.YOUTUBE
        if extract_vimeo_id(url):
            return VideoType.VIMEO
    except ValueError:  # e.g. "http://[::1"
        return VideoType.OTHER
    if url.strip().startswith("/upload/"):
        return VideoType.LOCAL
    return VideoType.OTHER
