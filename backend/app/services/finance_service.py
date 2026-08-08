from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.finance import Transaction
from app.models.comanda import Comanda
from app.schemas.finance import FinanceChart, FinanceChartPoint, FinanceSummary, TransactionCreate


def create_transaction(db: Session, data: TransactionCreate, owner_id: int) -> Transaction:
    if data.comanda_id is not None:
        comanda = (
            db.query(Comanda)
            .filter(Comanda.id == data.comanda_id, Comanda.owner_id == owner_id)
            .first()
        )
        if not comanda:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comanda não encontrada.")

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


def get_chart_data(db: Session, owner_id: int, months: int = 6) -> FinanceChart:
    """Agrega entradas e saídas por mês, para os últimos `months` meses."""
    now = datetime.now(timezone.utc)

    # Gera a lista dos últimos N períodos (ano-mês), do mais antigo pro mais recente.
    periodos = []
    ano, mes = now.year, now.month
    for _ in range(months):
        periodos.append(f"{ano:04d}-{mes:02d}")
        mes -= 1
        if mes == 0:
            mes = 12
            ano -= 1
    periodos.reverse()

    inicio = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30 * (months - 1))
    inicio = inicio.replace(day=1)

    transacoes = (
        db.query(Transaction)
        .filter(Transaction.owner_id == owner_id, Transaction.created_at >= inicio)
        .all()
    )

    agregados = {p: {"entradas": 0.0, "saidas": 0.0} for p in periodos}

    for t in transacoes:
        chave = t.created_at.strftime("%Y-%m")
        if chave in agregados:
            if t.type == "entrada":
                agregados[chave]["entradas"] += t.amount
            else:
                agregados[chave]["saidas"] += t.amount

    pontos = [
        FinanceChartPoint(periodo=p, entradas=agregados[p]["entradas"], saidas=agregados[p]["saidas"])
        for p in periodos
    ]

    return FinanceChart(pontos=pontos)
