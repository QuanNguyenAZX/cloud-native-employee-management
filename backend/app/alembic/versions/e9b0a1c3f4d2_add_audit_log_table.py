"""Add audit log table

Revision ID: e9b0a1c3f4d2
Revises: c2a9d0c8b7f1
Create Date: 2026-06-29 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e9b0a1c3f4d2"
down_revision = "c2a9d0c8b7f1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("actor_email", sa.String(length=255), nullable=True),
        sa.Column("actor_role", sa.String(length=20), nullable=True),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=True),
        sa.Column("detail", sa.String(length=255), nullable=False),
        sa.Column("before_data", sa.JSON(), nullable=True),
        sa.Column("after_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["user.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_log_actor_id"), "audit_log", ["actor_id"], unique=False
    )
    op.create_index(
        op.f("ix_audit_log_actor_email"), "audit_log", ["actor_email"], unique=False
    )
    op.create_index(
        op.f("ix_audit_log_actor_role"), "audit_log", ["actor_role"], unique=False
    )
    op.create_index(
        op.f("ix_audit_log_action"), "audit_log", ["action"], unique=False
    )
    op.create_index(
        op.f("ix_audit_log_entity_type"), "audit_log", ["entity_type"], unique=False
    )
    op.create_index(
        op.f("ix_audit_log_entity_id"), "audit_log", ["entity_id"], unique=False
    )
    op.create_index(
        op.f("ix_audit_log_created_at"), "audit_log", ["created_at"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_audit_log_created_at"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_entity_id"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_entity_type"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_action"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_actor_role"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_actor_email"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_actor_id"), table_name="audit_log")
    op.drop_table("audit_log")
