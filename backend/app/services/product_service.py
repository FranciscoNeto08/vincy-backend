from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product, StockMovement
from app.schemas.product import ProductCreate, ProductUpdate, StockMovementCreate


def _normalize_code(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _generate_sku() -> str:
    return f"VYN-{uuid4().hex[:10].upper()}"


def _ensure_unique_codes(db: Session, owner_id: int, sku: str | None, barcode: str | None, exclude_id: int | None = None) -> None:
    if sku:
        query = db.query(Product.id).filter(Product.owner_id == owner_id, func.lower(Product.sku) == sku.lower())
        if exclude_id is not None:
            query = query.filter(Product.id != exclude_id)
        if query.first():
            raise HTTPException(status_code=409, detail="Já existe um produto com este SKU.")

    if barcode:
        query = db.query(Product.id).filter(Product.owner_id == owner_id, Product.barcode == barcode)
        if exclude_id is not None:
            query = query.filter(Product.id != exclude_id)
        if query.first():
            raise HTTPException(status_code=409, detail="Já existe um produto com este código de barras.")


def create_product(db: Session, owner_id: int, user_id: int, data: ProductCreate) -> Product:
    payload = data.model_dump(exclude={"initial_quantity"})
    payload["barcode"] = _normalize_code(payload.get("barcode"))
    payload["sku"] = _normalize_code(payload.get("sku")) or _generate_sku()

    _ensure_unique_codes(db, owner_id, payload["sku"], payload["barcode"])

    product = Product(
        **payload,
        owner_id=owner_id,
        quantity=data.initial_quantity,
    )
    db.add(product)

    try:
        db.flush()

        if data.initial_quantity > 0:
            db.add(
                StockMovement(
                    owner_id=owner_id,
                    product_id=product.id,
                    user_id=user_id,
                    movement_type="entrada",
                    quantity=data.initial_quantity,
                    previous_quantity=0,
                    new_quantity=data.initial_quantity,
                    reason="Estoque inicial",
                )
            )

        db.commit()
        db.refresh(product)
        return product
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="SKU ou código de barras já cadastrado.") from exc


def list_products(
    db: Session,
    owner_id: int,
    search: str | None = None,
    stock_status: str | None = None,
    only_active: bool = True,
    limit: int = 500,
    offset: int = 0,
) -> list[Product]:
    query = db.query(Product).filter(Product.owner_id == owner_id)

    if only_active:
        query = query.filter(Product.active.is_(True))

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Product.name.ilike(term),
                Product.sku.ilike(term),
                Product.barcode.ilike(term),
                Product.category.ilike(term),
            )
        )

    if stock_status == "low":
        query = query.filter(Product.quantity > 0, Product.quantity <= Product.minimum_stock)
    elif stock_status == "out":
        query = query.filter(Product.quantity == 0)

    return query.order_by(Product.name.asc()).offset(offset).limit(limit).all()


def get_product(db: Session, owner_id: int, product_id: int, for_update: bool = False) -> Product:
    query = db.query(Product).filter(Product.id == product_id, Product.owner_id == owner_id)
    if for_update:
        query = query.with_for_update()
    product = query.first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return product


def get_product_by_barcode(db: Session, owner_id: int, barcode: str) -> Product:
    barcode = _normalize_code(barcode)
    if not barcode:
        raise HTTPException(status_code=400, detail="Código de barras inválido.")

    product = (
        db.query(Product)
        .filter(Product.owner_id == owner_id, Product.barcode == barcode, Product.active.is_(True))
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado para este código.")
    return product


def update_product(db: Session, owner_id: int, product_id: int, data: ProductUpdate) -> Product:
    product = get_product(db, owner_id, product_id)
    changes = data.model_dump(exclude_unset=True)

    if "sku" in changes:
        changes["sku"] = _normalize_code(changes["sku"]) or product.sku
    if "barcode" in changes:
        changes["barcode"] = _normalize_code(changes["barcode"])

    _ensure_unique_codes(
        db,
        owner_id,
        changes.get("sku", product.sku),
        changes.get("barcode", product.barcode),
        exclude_id=product.id,
    )

    for field, value in changes.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)
        return product
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="SKU ou código de barras já cadastrado.") from exc


def deactivate_product(db: Session, owner_id: int, product_id: int) -> None:
    product = get_product(db, owner_id, product_id)
    product.active = False
    db.commit()


def create_movement(db: Session, owner_id: int, user_id: int, product_id: int, data: StockMovementCreate) -> Product:
    try:
        product = get_product(db, owner_id, product_id, for_update=True)
        previous = int(product.quantity or 0)

        if data.movement_type in {"entrada", "saida"}:
            if data.quantity is None:
                raise HTTPException(status_code=422, detail="Informe a quantidade da movimentação.")
            quantity = int(data.quantity)
            new_quantity = previous + quantity if data.movement_type == "entrada" else previous - quantity
            if new_quantity < 0:
                raise HTTPException(status_code=409, detail=f"Estoque insuficiente. Disponível: {previous} unidade(s).")
        else:
            if data.target_quantity is None:
                raise HTTPException(status_code=422, detail="Informe a quantidade final do ajuste.")
            new_quantity = int(data.target_quantity)
            quantity = abs(new_quantity - previous)
            if quantity == 0:
                raise HTTPException(status_code=400, detail="O estoque informado já é o estoque atual.")

        product.quantity = new_quantity
        movement = StockMovement(
            owner_id=owner_id,
            product_id=product.id,
            user_id=user_id,
            movement_type=data.movement_type,
            quantity=quantity,
            previous_quantity=previous,
            new_quantity=new_quantity,
            reason=data.reason,
        )
        db.add(movement)
        db.commit()
        db.refresh(product)
        return product
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


def list_movements(db: Session, owner_id: int, product_id: int, limit: int = 100) -> list[StockMovement]:
    get_product(db, owner_id, product_id)
    return (
        db.query(StockMovement)
        .filter(StockMovement.owner_id == owner_id, StockMovement.product_id == product_id)
        .order_by(StockMovement.created_at.desc(), StockMovement.id.desc())
        .limit(limit)
        .all()
    )


def inventory_summary(db: Session, owner_id: int):
    products = db.query(Product).filter(Product.owner_id == owner_id, Product.active.is_(True)).all()
    return {
        "total_products": len(products),
        "total_units": sum(int(p.quantity or 0) for p in products),
        "low_stock": sum(1 for p in products if 0 < int(p.quantity or 0) <= int(p.minimum_stock or 0)),
        "out_of_stock": sum(1 for p in products if int(p.quantity or 0) == 0),
        "inventory_cost_value": round(sum(float(p.cost_price or 0) * int(p.quantity or 0) for p in products), 2),
        "inventory_sale_value": round(sum(float(p.sale_price or 0) * int(p.quantity or 0) for p in products), 2),
    }
