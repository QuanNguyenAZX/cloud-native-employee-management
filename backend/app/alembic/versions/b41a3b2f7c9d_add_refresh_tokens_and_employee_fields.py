"""Add refresh tokens and employee fields

Revision ID: b41a3b2f7c9d
Revises: 8f4d8d3f1b7a
Create Date: 2026-06-28 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "b41a3b2f7c9d"
down_revision = "8f4d8d3f1b7a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("employee", sa.Column("salary", sa.Float(), nullable=True))
    op.add_column("employee", sa.Column("birth_date", sa.Date(), nullable=True))

    op.create_table(
        "refresh_token",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("jti", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("token_type", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_refresh_token_jti"), "refresh_token", ["jti"], unique=True
    )
    op.create_index(
        op.f("ix_refresh_token_user_id"), "refresh_token", ["user_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_refresh_token_user_id"), table_name="refresh_token")
    op.drop_index(op.f("ix_refresh_token_jti"), table_name="refresh_token")
    op.drop_table("refresh_token")
    op.drop_column("employee", "birth_date")
    op.drop_column("employee", "salary")
