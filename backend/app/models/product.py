from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("owner_id", "sku", name="uq_products_owner_sku"),
        UniqueConstraint("owner_id", "barcode", name="uq_products_owner_barcode"),
        CheckConstraint("quantity >= 0", name="ck_products_quantity_nonnegative"),
        CheckConstraint("minimum_stock >= 0", name="ck_products_minimum_stock_nonnegative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String(150), nullable=False, index=True)
    sku = Column(String(64), nullable=False)
    barcode = Column(String(64), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    cost_price = Column(Float, nullable=False, default=0.0)
    sale_price = Column(Float, nullable=False, default=0.0)
    quantity = Column(Integer, nullable=False, default=0)
    minimum_stock = Column(Integer, nullable=False, default=0)
    active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    owner = relationship("User", foreign_keys=[owner_id])
    movements = relationship(
        "StockMovement",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="desc(StockMovement.created_at)",
    )


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_stock_movements_quantity_positive"),
        CheckConstraint("previous_quantity >= 0", name="ck_stock_movements_previous_nonnegative"),
        CheckConstraint("new_quantity >= 0", name="ck_stock_movements_new_nonnegative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    movement_type = Column(String(20), nullable=False, index=True)  # entrada | saida | ajuste
    quantity = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    product = relationship("Product", back_populates="movements")
