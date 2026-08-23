"""merge heads

Revision ID: 850f7086ffdd
Revises: 003_add_candidate_deleted_at, 25b9705eb8d5
Create Date: 2026-08-23 08:07:05.596843

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "850f7086ffdd"
down_revision: Union[str, Sequence[str], None] = (
    "003_add_candidate_deleted_at",
    "25b9705eb8d5",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
