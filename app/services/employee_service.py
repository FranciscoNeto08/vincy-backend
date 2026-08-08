from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate


def create_employee(
    db: Session,
    data: EmployeeCreate,
    owner_id: int,
) -> Employee:

    name = data.name.strip()

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe o nome do colaborador.",
        )

    employee = Employee(
        name=name,
        phone=data.phone.strip() if data.phone else None,
        email=str(data.email) if data.email else None,
        owner_id=owner_id,
        active=True,
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def list_employees(
    db: Session,
    owner_id: int,
) -> list[Employee]:

    return (
        db.query(Employee)
        .filter(
            Employee.owner_id == owner_id,
            Employee.active.is_(True),
        )
        .order_by(Employee.name.asc())
        .all()
    )


def get_employee(
    db: Session,
    employee_id: int,
    owner_id: int,
) -> Employee:

    employee = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.owner_id == owner_id,
        )
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado.",
        )

    return employee


def delete_employee(
    db: Session,
    employee_id: int,
    owner_id: int,
) -> None:
    """
    Não apagamos fisicamente o colaborador para preservar
    comandas antigas e o ranking/histórico.
    """

    employee = get_employee(db, employee_id, owner_id)

    employee.active = False

    db.commit()
