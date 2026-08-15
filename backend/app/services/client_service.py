from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate
from app.services.marketing_permission_service import set_permission


_PERMISSION_FIELDS = {
    "email_marketing_opt_in",
    "whatsapp_marketing_opt_in",
    "marketing_permission_source",
    "marketing_legal_basis_note",
}


def create_client(db: Session, data: ClientCreate, owner_id: int) -> Client:
    payload = data.model_dump()
    email_opt = bool(payload.pop("email_marketing_opt_in", False))
    whatsapp_opt = bool(payload.pop("whatsapp_marketing_opt_in", False))
    source = payload.pop("marketing_permission_source", "not_informed")
    basis_note = payload.pop("marketing_legal_basis_note", None)

    try:
        client = Client(**payload, owner_id=owner_id)
        db.add(client)
        db.flush()
        set_permission(
            db,
            owner_id=owner_id,
            client_id=client.id,
            channel="email",
            allowed=email_opt,
            source=source,
            legal_basis_note=basis_note,
            commit=False,
        )
        set_permission(
            db,
            owner_id=owner_id,
            client_id=client.id,
            channel="whatsapp",
            allowed=whatsapp_opt,
            source=source,
            legal_basis_note=basis_note,
            commit=False,
        )
        db.commit()
        db.refresh(client)
        return client
    except Exception:
        db.rollback()
        raise


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
    fields_set = set(data.model_fields_set)
    payload = data.model_dump(exclude_unset=True)

    email_opt = payload.pop("email_marketing_opt_in", None)
    whatsapp_opt = payload.pop("whatsapp_marketing_opt_in", None)
    source = payload.pop("marketing_permission_source", None) or "manual"
    basis_note = payload.pop("marketing_legal_basis_note", None)

    for field, value in payload.items():
        setattr(client, field, value)

    try:
        if "email_marketing_opt_in" in fields_set:
            set_permission(
                db,
                owner_id=owner_id,
                client_id=client.id,
                channel="email",
                allowed=bool(email_opt),
                source=source,
                legal_basis_note=basis_note,
                commit=False,
            )
            if email_opt:
                client.unsubscribed = False
        if "whatsapp_marketing_opt_in" in fields_set:
            set_permission(
                db,
                owner_id=owner_id,
                client_id=client.id,
                channel="whatsapp",
                allowed=bool(whatsapp_opt),
                source=source,
                legal_basis_note=basis_note,
                commit=False,
            )
        db.commit()
        db.refresh(client)
        return client
    except Exception:
        db.rollback()
        raise


def delete_client(db: Session, client_id: int, owner_id: int) -> None:
    client = get_client(db, client_id, owner_id)
    db.delete(client)
    db.commit()
