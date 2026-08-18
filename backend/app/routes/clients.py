from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_subscriber
from app.models.user import User
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from app.services import client_service

router = APIRouter(prefix="/clients", tags=["Clientes"])


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return client_service.create_client(db, data, owner_id=current_user.id)


@router.get("", response_model=list[ClientResponse])
def list_clients(
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return client_service.list_clients(db, owner_id=current_user.id, search=search)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return client_service.get_client(db, client_id, owner_id=current_user.id)


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return client_service.update_client(db, client_id, data, owner_id=current_user.id)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    client_service.delete_client(db, client_id, owner_id=current_user.id)
