"""legal acceptance and subscription gate
Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
"""
from alembic import op
import sqlalchemy as sa
revision = "c4d5e6f7a8b9"
down_revision = "b2c3d4e5f6a7"
branch_labels=None
depends_on=None
def upgrade():
    op.add_column("users", sa.Column("subscription_status", sa.String(20), nullable=False, server_default="pending"))
    op.add_column("users", sa.Column("subscription_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("subscription_activated_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_users_subscription_status", "users", ["subscription_status"])
    op.add_column("comandas", sa.Column("feedback_token_hash", sa.String(64), nullable=True))
    op.add_column("comandas", sa.Column("feedback_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("comandas", sa.Column("feedback_rating", sa.Integer(), nullable=True))
    op.add_column("comandas", sa.Column("feedback_comment", sa.Text(), nullable=True))
    op.add_column("comandas", sa.Column("feedback_responded_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_comandas_feedback_token_hash", "comandas", ["feedback_token_hash"], unique=True)
    op.create_table("legal_acceptances",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("terms_version", sa.String(30), nullable=False), sa.Column("privacy_version", sa.String(30), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ip", sa.String(64)), sa.Column("user_agent", sa.String(255)), sa.Column("request_id", sa.String(100)))
    op.create_index("ix_legal_acceptances_user_id", "legal_acceptances", ["user_id"])
def downgrade():
    op.drop_index("ix_comandas_feedback_token_hash", table_name="comandas")
    op.drop_column("comandas","feedback_responded_at"); op.drop_column("comandas","feedback_comment"); op.drop_column("comandas","feedback_rating"); op.drop_column("comandas","feedback_expires_at"); op.drop_column("comandas","feedback_token_hash")
    op.drop_index("ix_legal_acceptances_user_id", table_name="legal_acceptances"); op.drop_table("legal_acceptances")
    op.drop_index("ix_users_subscription_status", table_name="users")
    op.drop_column("users","subscription_activated_at"); op.drop_column("users","subscription_expires_at"); op.drop_column("users","subscription_status")
