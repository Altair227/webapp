from .base import Base

# from typing import TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

# if TYPE_CHECKING:
#      from .admin_data import AdminData


class News(Base):
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
