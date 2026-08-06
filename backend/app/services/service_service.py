from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate


def create_service(db: Session, data: ServiceCreate, owner_id: int) -> Service:
    service = Service(**data.model_dump(), owner_id=owner_id)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def list_services(db: Session, owner_id: int, only_active: bool = False) -> list[Service]:
    query = db.query(Service).filter(Service.owner_id == owner_id)
    if only_active:
        query = query.filter(Service.active.is_(True))
    return query.order_by(Service.name).all()


def get_service(db: Session, service_id: int, owner_id: int) -> Service:
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.owner_id == owner_id)
        .first()
    )
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado.")
    return service


def update_service(db: Session, service_id: int, data: ServiceUpdate, owner_id: int) -> Service:
    service = get_service(db, service_id, owner_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)
    return service


def delete_service(db: Session, service_id: int, owner_id: int) -> None:
    service = get_service(db, service_id, owner_id)
    db.delete(service)
    db.commit()
