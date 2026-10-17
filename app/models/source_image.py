from .media import Media
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class SourceImage(Media):
    __tablename__ = "source_image"

    id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="CASCADE"),
        primary_key=True,
        comment="",
    )

    url: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="",
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        default=None,
        nullable=True,
        comment="",
    )

    extension: Mapped[str] = mapped_column(
        String(5),
        default=None,
        nullable=True,
        comment="",
    )

    size: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=True,
        comment="",
    )
    __mapper_args__ = {"polymorphic_identity": "image"}
