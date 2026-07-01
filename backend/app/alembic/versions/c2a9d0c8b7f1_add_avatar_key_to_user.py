"""Add avatar key to user

Revision ID: c2a9d0c8b7f1
Revises: b41a3b2f7c9d
Create Date: 2026-06-28 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c2a9d0c8b7f1"
down_revision = "b41a3b2f7c9d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("avatar_key", sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column("user", "avatar_key")
