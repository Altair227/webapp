from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.types import SmallIntEnum, VideoType
from app.utils.dummy_image import dummy_image

from .base import Base, SafeDeleteMixin, TimestampMixin


class SourceVideo(Base, TimestampMixin, SafeDeleteMixin):
    __tablename__ = "source_video"
    __table_args__ = (SmallIntEnum.create_check_constraint("type", VideoType),)

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
        default=None,
        nullable=True,
        comment="",
    )
    # None: not detected yet
    type: Mapped[VideoType | None] = mapped_column(
        SmallIntEnum(VideoType),
        default=None,
        nullable=True,
        comment="",
    )
    # real picture only, the placeholder is never stored (see cover)
    poster: Mapped[str | None] = mapped_column(
        String(500),
        default=None,
        nullable=True,
        comment="",
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        comment="",
    )
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
        comment="",
    )

    @property
    def cover(self) -> str:
        """Saved poster, or a placeholder when there is none."""
        if self.poster:
            return self.poster
        if self.type == VideoType.OTHER:
            return dummy_image(self.filename or "Video")
        return dummy_image("Processing")
