"""add_admins_type_check

Revision ID: 863773b4a9f0
Revises: d902b404e4bf
Create Date: 2026-10-22 02:07:51.325737

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "863773b4a9f0"
down_revision: Union[str, Sequence[str], None] = "d902b404e4bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_type_valid_values",
        "admins",
        "type IN (0, 1, 2)",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_type_valid_values", "admins", type_="check")
