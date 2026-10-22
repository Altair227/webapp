from .base import Base, TimestampMixin, SafeDeleteMixin
from .relations import _r_news_source_image
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .source_image import SourceImage


class News(Base, TimestampMixin, SafeDeleteMixin):
    __tablename__ = "news"

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="",
    )
    content: Mapped[bool] = mapped_column(
        Text,
        nullable=False,
        comment="",
    )
    published_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="",
    )
    image_url: Mapped[str] = mapped_column(
        String(255),
        default=None,
        nullable=True,
        comment="",
    )
    images: Mapped[list["SourceImage"]] = relationship(
        "SourceImage",
        secondary=_r_news_source_image,
        lazy="select",
        passive_deletes=True,
    )
