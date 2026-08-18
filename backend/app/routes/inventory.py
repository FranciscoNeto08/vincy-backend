from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_subscriber
from app.models.user import User
from app.schemas.product import (
    InventorySummary,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    StockMovementCreate,
    StockMovementResponse,
)
from app.services import product_service

router = APIRouter(prefix="/inventory", tags=["Estoque"])


@router.get("/summary", response_model=InventorySummary)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return product_service.inventory_summary(db, current_user.id)


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return product_service.create_product(db, current_user.id, current_user.id, data)


@router.get("/products", response_model=list[ProductResponse])
def list_products(
    search: str | None = Query(default=None, max_length=150),
    stock_status: str | None = Query(default=None, pattern="^(low|out)$"),
    only_active: bool = True,
    limit: int = Query(default=500, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return product_service.list_products(
        db,
        current_user.id,
        search=search,
        stock_status=stock_status,
        only_active=only_active,
        limit=limit,
        offset=offset,
    )


@router.get("/products/barcode/{barcode}", response_model=ProductResponse)
def get_by_barcode(
    barcode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return product_service.get_product_by_barcode(db, current_user.id, barcode)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return product_service.get_product(db, current_user.id, product_id)


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return product_service.update_product(db, current_user.id, product_id, data)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    product_service.deactivate_product(db, current_user.id, product_id)


@router.post("/products/{product_id}/movements", response_model=ProductResponse)
def move_stock(
    product_id: int,
    data: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return product_service.create_movement(db, current_user.id, current_user.id, product_id, data)


@router.get("/products/{product_id}/movements", response_model=list[StockMovementResponse])
def list_movements(
    product_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return product_service.list_movements(db, current_user.id, product_id, limit=limit)
