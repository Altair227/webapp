from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, SafeDeleteMixin, TimestampMixin


class SourceImage(Base, TimestampMixin, SafeDeleteMixin):
    __tablename__ = "source_image"

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
