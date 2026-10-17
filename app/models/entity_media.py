from typing import TYPE_CHECKING
from .base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .entity import Entity
    from .media import Media


class EntityMedia(Base):
    __tablename__ = "entity_media"

    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        primary_key=True,
    )

    media_id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="CASCADE"),
        primary_key=True,
    )

    entity: Mapped["Entity"] = relationship(
        back_populates="entity_media_links",
    )

    media: Mapped["Media"] = relationship(
        back_populates="entity_media_links",
    )
