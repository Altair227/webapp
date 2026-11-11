from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SafeDeleteMixin, TimestampMixin
from .relations import _r_news_source_image


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
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="",
    )
    # None: visible on the site right away (created_at is used instead)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
        comment="",
    )
    image_url: Mapped[str | None] = mapped_column(
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
        order_by="SourceImage.id",
    )
