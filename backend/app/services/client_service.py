from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


def create_client(db: Session, data: ClientCreate, owner_id: int) -> Client:
    client = Client(**data.model_dump(), owner_id=owner_id)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def list_clients(db: Session, owner_id: int, search: str | None = None) -> list[Client]:
    query = db.query(Client).filter(Client.owner_id == owner_id)
    if search:
        query = query.filter(Client.name.ilike(f"%{search}%"))
    return query.order_by(Client.name).all()


def get_client(db: Session, client_id: int, owner_id: int) -> Client:
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.owner_id == owner_id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    return client


def update_client(db: Session, client_id: int, data: ClientUpdate, owner_id: int) -> Client:
    client = get_client(db, client_id, owner_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client_id: int, owner_id: int) -> None:
    client = get_client(db, client_id, owner_id)
    db.delete(client)
    db.commit()
