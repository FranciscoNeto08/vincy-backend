from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.history import History
from app.models.user import User
from app.schemas.comanda import ComandaCreate, ComandaItemCreate, ComandaResponse
from app.schemas.history import HistoryResponse
from app.services import comanda_service

router = APIRouter(prefix="/comandas", tags=["Comandas"])


@router.post("", response_model=ComandaResponse, status_code=status.HTTP_201_CREATED)
def open_comanda(
    data: ComandaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return comanda_service.open_comanda(db, data, current_user)


@router.get("", response_model=list[ComandaResponse])
def list_comandas(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return comanda_service.list_comandas(db, owner_id=current_user.id, status_filter=status_filter)


@router.get("/{comanda_id}", response_model=ComandaResponse)
def get_comanda(
    comanda_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return comanda_service.get_comanda(db, comanda_id, owner_id=current_user.id)


@router.post("/{comanda_id}/items", response_model=ComandaResponse)
def add_service(
    comanda_id: int,
    item_data: ComandaItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return comanda_service.add_service_to_comanda(db, comanda_id, item_data, current_user)


@router.post("/{comanda_id}/finalizar", response_model=ComandaResponse)
def finalize_comanda(
    comanda_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return comanda_service.finalize_comanda(db, comanda_id, current_user)


@router.post("/{comanda_id}/cancelar", response_model=ComandaResponse)
def cancel_comanda(
    comanda_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return comanda_service.cancel_comanda(db, comanda_id, current_user)


@router.delete("/historico", status_code=status.HTTP_204_NO_CONTENT)
def clear_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Apaga todas as comandas finalizadas (botão 'Limpar histórico')."""
    comanda_service.delete_all_history(db, owner_id=current_user.id)


@router.get("/{comanda_id}/historico", response_model=list[HistoryResponse])
def get_comanda_history(
    comanda_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # garante que a comanda pertence ao usuário antes de expor o histórico
    comanda_service.get_comanda(db, comanda_id, owner_id=current_user.id)

    return (
        db.query(History)
        .filter(History.comanda_id == comanda_id, History.owner_id == current_user.id)
        .order_by(History.data.desc())
        .all()
    )
