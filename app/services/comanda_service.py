from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.comanda import Comanda, ComandaItem
from app.models.employee import Employee
from app.models.history import History
from app.models.service import Service
from app.models.user import User
from app.schemas.comanda import ComandaCreate, ComandaItemCreate


def _log_history(
    db: Session,
    comanda_id: int,
    action: str,
    user: User,
    owner_id: int,
) -> None:
    db.add(
        History(
            comanda_id=comanda_id,
            action=action,
            usuario=user.name,
            owner_id=owner_id,
        )
    )


def _get_or_create_service(
    db: Session,
    name: str,
    price: float,
    owner_id: int,
) -> Service:
    """Reaproveita um serviço já cadastrado com o mesmo nome, ou cria um novo."""

    service = (
        db.query(Service)
        .filter(
            Service.owner_id == owner_id,
            Service.name == name,
        )
        .first()
    )

    if service:
        service.price = price
        return service

    service = Service(
        name=name,
        price=price,
        owner_id=owner_id,
    )

    db.add(service)
    db.flush()

    return service


def open_comanda(
    db: Session,
    data: ComandaCreate,
    user: User,
) -> Comanda:

    client = (
        db.query(Client)
        .filter(
            Client.id == data.client_id,
            Client.owner_id == user.id,
        )
        .first()
    )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado.",
        )

    employee = (
        db.query(Employee)
        .filter(
            Employee.id == data.employee_id,
            Employee.owner_id == user.id,
            Employee.active.is_(True),
        )
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado ou inativo.",
        )

    comanda = Comanda(
        client_id=client.id,
        user_id=user.id,
        employee_id=employee.id,
        owner_id=user.id,
        status="aberta",
        total=0.0,
    )

    db.add(comanda)
    db.flush()

    _log_history(
        db,
        comanda.id,
        f"comanda aberta - colaborador: {employee.name}",
        user,
        user.id,
    )

    db.commit()
    db.refresh(comanda)

    return comanda


def get_comanda(
    db: Session,
    comanda_id: int,
    owner_id: int,
) -> Comanda:

    comanda = (
        db.query(Comanda)
        .filter(
            Comanda.id == comanda_id,
            Comanda.owner_id == owner_id,
        )
        .first()
    )

    if not comanda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comanda não encontrada.",
        )

    return comanda


def list_comandas(
    db: Session,
    owner_id: int,
    status_filter: str | None = None,
) -> list[Comanda]:

    query = (
        db.query(Comanda)
        .filter(Comanda.owner_id == owner_id)
    )

    if status_filter:
        query = query.filter(
            Comanda.status == status_filter
        )

    return (
        query
        .order_by(Comanda.data_abertura.desc())
        .all()
    )


def add_service_to_comanda(
    db: Session,
    comanda_id: int,
    item_data: ComandaItemCreate,
    user: User,
) -> Comanda:

    comanda = get_comanda(
        db,
        comanda_id,
        user.id,
    )

    if comanda.status != "aberta":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível adicionar serviços em comandas abertas.",
        )

    service = _get_or_create_service(
        db,
        item_data.name,
        item_data.price,
        user.id,
    )

    item = ComandaItem(
        comanda_id=comanda.id,
        service_id=service.id,
        name=item_data.name,
        price=item_data.price,
        quantity=item_data.quantity,
    )

    db.add(item)

    comanda.total = (
        comanda.total +
        (item_data.price * item_data.quantity)
    )

    _log_history(
        db,
        comanda.id,
        f"serviço '{item_data.name}' adicionado",
        user,
        user.id,
    )

    db.commit()
    db.refresh(comanda)

    return comanda


def finalize_comanda(
    db: Session,
    comanda_id: int,
    user: User,
) -> Comanda:

    comanda = get_comanda(
        db,
        comanda_id,
        user.id,
    )

    if comanda.status != "aberta":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Somente comandas abertas podem ser finalizadas.",
        )

    if not comanda.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível finalizar uma comanda sem serviços.",
        )

    comanda.status = "finalizada"
    comanda.data_fechamento = datetime.now(timezone.utc)

    _log_history(
        db,
        comanda.id,
        "atendimento finalizado",
        user,
        user.id,
    )

    db.commit()
    db.refresh(comanda)

    return comanda


def cancel_comanda(
    db: Session,
    comanda_id: int,
    user: User,
) -> Comanda:

    comanda = get_comanda(
        db,
        comanda_id,
        user.id,
    )

    if comanda.status != "aberta":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Somente comandas abertas podem ser canceladas.",
        )

    comanda.status = "cancelada"
    comanda.data_fechamento = datetime.now(timezone.utc)

    _log_history(
        db,
        comanda.id,
        "comanda cancelada",
        user,
        user.id,
    )

    db.commit()
    db.refresh(comanda)

    return comanda


def delete_all_history(
    db: Session,
    owner_id: int,
) -> None:
    """Apaga todas as comandas finalizadas do usuário."""

    db.query(Comanda).filter(
        Comanda.owner_id == owner_id,
        Comanda.status == "finalizada",
    ).delete()

    db.commit()
