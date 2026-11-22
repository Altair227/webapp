import re
from urllib.parse import parse_qs, urlparse

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, SafeDeleteMixin, TimestampMixin


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


class SourceVideo(Base, TimestampMixin, SafeDeleteMixin):
    __tablename__ = "source_video"

    url: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="",
    )
    filename: Mapped[str | None] = mapped_column(
        String(255),
        default=None,
        nullable=True,
        comment="",
    )
    extension: Mapped[str | None] = mapped_column(
        String(5),
        default=None,
        nullable=True,
        comment="",
    )
    size: Mapped[int | None] = mapped_column(
        Integer,
        default=0,
        nullable=True,
        comment="",
    )
    duration: Mapped[int | None] = mapped_column(
        Integer,
        default=0,
        nullable=True,
        comment="",
    )

    @property
    def poster(self) -> str | None:
        video_id = extract_youtube_id(self.url)
        if not video_id:
            return None
        return f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
