from .base import Base
from app.common.types import EntityType, SmallIntEnum, EmailTokenType
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from datetime import datetime


class EmailToken(Base):
    __tablename__ = "email_tokens"
    __table_args__ = (
        SmallIntEnum.create_check_constraint("entity_type", EntityType),
        SmallIntEnum.create_check_constraint("type", EmailTokenType),
    )
    entity_type: Mapped[EntityType] = mapped_column(
        SmallIntEnum(EntityType),
        nullable=False,
        comment="Owner type",
    )
    entity_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Owner type",
    )
    token: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    type: Mapped[EmailTokenType] = mapped_column(
        SmallIntEnum(EmailTokenType),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
