"""Association tables for N:M relations (_r_<left>_<right>)."""

from sqlalchemy import Column, ForeignKey, Table

from .base import Base


_r_news_source_image = Table(
    "_r_news_source_image",
    Base.metadata,
    Column(
        "news_id",
        ForeignKey("news.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "source_image_id",
        ForeignKey("source_image.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)
