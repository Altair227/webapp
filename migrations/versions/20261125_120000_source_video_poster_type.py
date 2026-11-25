"""source video poster and type

Revision ID: 3c9d71a4e0b2
Revises: f5e24b13c8e6
Create Date: 2026-11-25 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3c9d71a4e0b2"
down_revision: Union[str, Sequence[str], None] = "f5e24b13c8e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "source_video", sa.Column("type", sa.SmallInteger(), nullable=True)
    )
    op.add_column(
        "source_video",
        sa.Column("poster", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "source_video",
        sa.Column(
            "attempts", sa.Integer(), server_default="0", nullable=False
        ),
    )
    op.add_column(
        "source_video",
        sa.Column(
            "next_attempt_at", sa.DateTime(timezone=True), nullable=True
        ),
    )
    # autogenerate does not detect CHECK constraints
    op.create_check_constraint(
        "ck_type_valid_values",
        "source_video",
        "type IN (0, 1, 2, 3)",
    )
    # 0 meant "unknown": it was the model default
    op.execute("UPDATE source_video SET duration = NULL WHERE duration = 0")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_type_valid_values", "source_video", type_="check")
    op.drop_column("source_video", "next_attempt_at")
    op.drop_column("source_video", "attempts")
    op.drop_column("source_video", "poster")
    op.drop_column("source_video", "type")
