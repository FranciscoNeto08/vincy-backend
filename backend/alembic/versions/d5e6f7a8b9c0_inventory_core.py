"""inventory core

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
"""
from alembic import op
import sqlalchemy as sa

revision = "d5e6f7a8b9c0"
down_revision = "c4d5e6f7a8b9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("barcode", sa.String(length=64), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cost_price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("sale_price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("minimum_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("owner_id", "sku", name="uq_products_owner_sku"),
        sa.UniqueConstraint("owner_id", "barcode", name="uq_products_owner_barcode"),
        sa.CheckConstraint("quantity >= 0", name="ck_products_quantity_nonnegative"),
        sa.CheckConstraint("minimum_stock >= 0", name="ck_products_minimum_stock_nonnegative"),
    )
    op.create_index("ix_products_id", "products", ["id"])
    op.create_index("ix_products_owner_id", "products", ["owner_id"])
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_owner_barcode_lookup", "products", ["owner_id", "barcode"])
    op.create_index("ix_products_owner_name_lookup", "products", ["owner_id", "name"])

    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("movement_type", sa.String(length=20), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("previous_quantity", sa.Integer(), nullable=False),
        sa.Column("new_quantity", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_stock_movements_quantity_positive"),
        sa.CheckConstraint("previous_quantity >= 0", name="ck_stock_movements_previous_nonnegative"),
        sa.CheckConstraint("new_quantity >= 0", name="ck_stock_movements_new_nonnegative"),
    )
    op.create_index("ix_stock_movements_id", "stock_movements", ["id"])
    op.create_index("ix_stock_movements_owner_id", "stock_movements", ["owner_id"])
    op.create_index("ix_stock_movements_product_id", "stock_movements", ["product_id"])
    op.create_index("ix_stock_movements_user_id", "stock_movements", ["user_id"])
    op.create_index("ix_stock_movements_movement_type", "stock_movements", ["movement_type"])
    op.create_index("ix_stock_movements_created_at", "stock_movements", ["created_at"])
    op.create_index("ix_stock_movements_product_created", "stock_movements", ["product_id", "created_at"])


def downgrade():
    op.drop_index("ix_stock_movements_product_created", table_name="stock_movements")
    op.drop_index("ix_stock_movements_created_at", table_name="stock_movements")
    op.drop_index("ix_stock_movements_movement_type", table_name="stock_movements")
    op.drop_index("ix_stock_movements_user_id", table_name="stock_movements")
    op.drop_index("ix_stock_movements_product_id", table_name="stock_movements")
    op.drop_index("ix_stock_movements_owner_id", table_name="stock_movements")
    op.drop_index("ix_stock_movements_id", table_name="stock_movements")
    op.drop_table("stock_movements")
    op.drop_index("ix_products_owner_name_lookup", table_name="products")
    op.drop_index("ix_products_owner_barcode_lookup", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_index("ix_products_owner_id", table_name="products")
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")
