from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_subscriber
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.services import employee_service


router = APIRouter(
    prefix="/employees",
    tags=["Equipe"],
)


@router.get(
    "",
    response_model=list[EmployeeResponse],
)
def list_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return employee_service.list_employees(
        db,
        owner_id=current_user.id,
    )


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return employee_service.create_employee(
        db,
        data,
        owner_id=current_user.id,
    )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    employee_service.delete_employee(
        db,
        employee_id,
        owner_id=current_user.id,
    )
