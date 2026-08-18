from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_subscriber
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate
from app.services import service_service

router = APIRouter(prefix="/services", tags=["Serviços"])


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return service_service.create_service(db, data, owner_id=current_user.id)


@router.get("", response_model=list[ServiceResponse])
def list_services(
    only_active: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return service_service.list_services(db, owner_id=current_user.id, only_active=only_active)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return service_service.get_service(db, service_id, owner_id=current_user.id)


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return service_service.update_service(db, service_id, data, owner_id=current_user.id)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    service_service.delete_service(db, service_id, owner_id=current_user.id)
