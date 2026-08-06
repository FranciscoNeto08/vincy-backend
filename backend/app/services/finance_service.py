from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.finance import Transaction
from app.schemas.finance import FinanceSummary, TransactionCreate


def create_transaction(db: Session, data: TransactionCreate, owner_id: int) -> Transaction:
    transaction = Transaction(**data.model_dump(), owner_id=owner_id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def list_transactions(db: Session, owner_id: int, type_filter: str | None = None) -> list[Transaction]:
    query = db.query(Transaction).filter(Transaction.owner_id == owner_id)
    if type_filter:
        query = query.filter(Transaction.type == type_filter)
    return query.order_by(Transaction.created_at.desc()).all()


def get_summary(db: Session, owner_id: int) -> FinanceSummary:
    entradas = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter(Transaction.owner_id == owner_id, Transaction.type == "entrada")
        .scalar()
    )
    saidas = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter(Transaction.owner_id == owner_id, Transaction.type == "saida")
        .scalar()
    )

    return FinanceSummary(
        total_entradas=entradas,
        total_saidas=saidas,
        lucro=entradas - saidas,
    )
