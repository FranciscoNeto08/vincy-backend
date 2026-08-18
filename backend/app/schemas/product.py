from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    barcode: str | None = Field(default=None, max_length=64)
    sku: str | None = Field(default=None, max_length=64)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    cost_price: float = Field(default=0, ge=0, le=100_000_000, allow_inf_nan=False)
    sale_price: float = Field(default=0, ge=0, le=100_000_000, allow_inf_nan=False)
    minimum_stock: int = Field(default=0, ge=0, le=10_000_000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("Nome do produto é obrigatório.")
        return value

    @field_validator("barcode", "sku", "category", "description")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class ProductCreate(ProductBase):
    initial_quantity: int = Field(default=0, ge=0, le=10_000_000)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    barcode: str | None = Field(default=None, max_length=64)
    sku: str | None = Field(default=None, max_length=64)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    cost_price: float | None = Field(default=None, ge=0, le=100_000_000, allow_inf_nan=False)
    sale_price: float | None = Field(default=None, ge=0, le=100_000_000, allow_inf_nan=False)
    minimum_stock: int | None = Field(default=None, ge=0, le=10_000_000)
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("Nome do produto é obrigatório.")
        return value

    @field_validator("barcode", "sku", "category", "description")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class ProductResponse(ProductBase):
    id: int
    owner_id: int
    sku: str
    quantity: int
    active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StockMovementCreate(BaseModel):
    movement_type: Literal["entrada", "saida", "ajuste"]
    quantity: int | None = Field(default=None, gt=0, le=10_000_000)
    target_quantity: int | None = Field(default=None, ge=0, le=10_000_000)
    reason: str | None = Field(default=None, max_length=255)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = " ".join(value.strip().split())
        return value or None


class StockMovementResponse(BaseModel):
    id: int
    owner_id: int
    product_id: int
    user_id: int
    movement_type: str
    quantity: int
    previous_quantity: int
    new_quantity: int
    reason: str | None
    reference_type: str | None
    reference_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventorySummary(BaseModel):
    total_products: int
    total_units: int
    low_stock: int
    out_of_stock: int
    inventory_cost_value: float
    inventory_sale_value: float
