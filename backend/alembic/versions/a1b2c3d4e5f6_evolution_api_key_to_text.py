"""change evolution api key to text

Revision ID: a1b2c3d4e5f6
Revises: f7c2d9e4a111
"""

from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "f7c2d9e4a111"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "evolution_configs",
        "api_key",
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "evolution_configs",
        "api_key",
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )