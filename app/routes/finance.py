from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.user import User
from app.schemas.finance import FinanceChart, FinanceSummary, TransactionCreate, TransactionResponse
from app.services import finance_service

router = APIRouter(prefix="/finance", tags=["Financeiro"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return finance_service.create_transaction(db, data, owner_id=current_user.id)


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    type_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return finance_service.list_transactions(db, owner_id=current_user.id, type_filter=type_filter)


@router.get("/resumo", response_model=FinanceSummary)
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return finance_service.get_summary(db, owner_id=current_user.id)


@router.get("/grafico", response_model=FinanceChart)
def get_chart(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return finance_service.get_chart_data(db, owner_id=current_user.id, months=months)
