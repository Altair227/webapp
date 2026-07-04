"""update format published at

Revision ID: 1403369b892e
Revises: 8d265a0a596d
Create Date: 2026-06-10 08:15:33.396698

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1403369b892e"
down_revision: Union[str, Sequence[str], None] = "8d265a0a596d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "news",
        "published_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        comment="",
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "news",
        "published_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        comment=None,
        existing_comment="",
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )
