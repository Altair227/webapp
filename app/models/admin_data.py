from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SafeDeleteMixin, TimestampMixin


if TYPE_CHECKING:
    from .admin import Admin


class AdminData(Base, TimestampMixin, SafeDeleteMixin):
    __tablename__ = "admin_data"

    admin_id: Mapped[int] = mapped_column(
        ForeignKey(
            "admins.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        comment="",
    )
    firstname: Mapped[str | None] = mapped_column(
        String(100),
        comment="",
        nullable=True,
    )
    lastname: Mapped[str | None] = mapped_column(
        String(100),
        comment="",
        nullable=True,
    )
    photo_url: Mapped[str | None] = mapped_column(
        String(500),
        comment="",
        nullable=True,
    )
    admin: Mapped["Admin"] = relationship(
        "Admin",
        back_populates="data",
    )
