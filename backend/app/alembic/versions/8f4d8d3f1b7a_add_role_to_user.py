"""Add role to user

Revision ID: 8f4d8d3f1b7a
Revises: 3b7e2e91f6c4
Create Date: 2026-06-24 15:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f4d8d3f1b7a"
down_revision = "3b7e2e91f6c4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="employee",
        ),
    )
    op.execute(
        "UPDATE \"user\" SET role = 'admin' WHERE is_superuser = true OR role = 'admin'"
    )
    op.alter_column("user", "role", server_default=None)


def downgrade():
    op.drop_column("user", "role")
