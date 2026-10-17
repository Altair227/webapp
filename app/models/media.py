from typing import TYPE_CHECKING
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String


if TYPE_CHECKING:
    from .entity_media import EntityMedia


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)

    type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    entity_media_links: Mapped[list["EntityMedia"]] = relationship(
        back_populates="media",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "media",
    }
