"""merge risk override and demographics migrations

Revision ID: 0815c4559f37
Revises: 003_add_risk_override_audit, ba062b2def4d
Create Date: 2026-08-20 19:56:07.964445

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "0815c4559f37"
down_revision: str | Sequence[str] | None = (
    "003_add_risk_override_audit",
    "ba062b2def4d",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
