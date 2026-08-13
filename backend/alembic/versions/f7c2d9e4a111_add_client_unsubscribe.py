"""add client unsubscribe flag"""
from alembic import op
import sqlalchemy as sa

revision = "f7c2d9e4a111"
down_revision = "e5a9b8c7d612"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("clients", sa.Column("unsubscribed", sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    op.drop_column("clients", "unsubscribed")
