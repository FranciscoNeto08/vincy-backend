"""legal acceptances, marketing permissions and privacy governance

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
"""
from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "legal_acceptances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("document_type", sa.String(length=30), nullable=False),
        sa.Column("document_version", sa.String(length=30), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_legal_acceptances_user_id", "legal_acceptances", ["user_id"])
    op.create_index("ix_legal_acceptances_document_type", "legal_acceptances", ["document_type"])
    op.create_unique_constraint(
        "uq_legal_acceptance_user_doc_version",
        "legal_acceptances",
        ["user_id", "document_type", "document_version"],
    )

    op.create_table(
        "client_marketing_permissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("allowed", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("source", sa.String(length=50), server_default="not_informed", nullable=False),
        sa.Column("legal_basis_note", sa.String(length=255), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("client_id", "channel", name="uq_client_marketing_permission_channel"),
    )
    op.create_index("ix_client_marketing_permissions_client_id", "client_marketing_permissions", ["client_id"])
    op.create_index("ix_client_marketing_permissions_owner_id", "client_marketing_permissions", ["owner_id"])
    op.create_index("ix_client_marketing_permissions_channel", "client_marketing_permissions", ["channel"])


def downgrade():
    op.drop_index("ix_client_marketing_permissions_channel", table_name="client_marketing_permissions")
    op.drop_index("ix_client_marketing_permissions_owner_id", table_name="client_marketing_permissions")
    op.drop_index("ix_client_marketing_permissions_client_id", table_name="client_marketing_permissions")
    op.drop_table("client_marketing_permissions")
    op.drop_constraint("uq_legal_acceptance_user_doc_version", "legal_acceptances", type_="unique")
    op.drop_index("ix_legal_acceptances_document_type", table_name="legal_acceptances")
    op.drop_index("ix_legal_acceptances_user_id", table_name="legal_acceptances")
    op.drop_table("legal_acceptances")
