from .base import Base
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from .entity_media import EntityMedia


class Entity(Base):
    __tablename__ = "entities"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    entity_media_links: Mapped[list["EntityMedia"]] = relationship(
        back_populates="entity",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "entity",
    }
