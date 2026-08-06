from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.client import Client
from app.models.service import Service
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


def _to_response_dict(appt: Appointment) -> dict:
    return {
        "id": appt.id,
        "client_id": appt.client_id,
        "service_id": appt.service_id,
        "client_name": appt.client.name if appt.client else None,
        "service_name": appt.service.name if appt.service else None,
        "scheduled_at": appt.scheduled_at,
        "reminder_minutes_before": appt.reminder_minutes_before,
        "notes": appt.notes,
        "status": appt.status,
        "notified": appt.notified,
        "created_at": appt.created_at,
    }


def create_appointment(db: Session, data: AppointmentCreate, owner_id: int) -> dict:
    client = (
        db.query(Client)
        .filter(Client.id == data.client_id, Client.owner_id == owner_id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")

    if data.service_id:
        service = (
            db.query(Service)
            .filter(Service.id == data.service_id, Service.owner_id == owner_id)
            .first()
        )
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado.")

    appt = Appointment(**data.model_dump(), owner_id=owner_id)
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return _to_response_dict(appt)


def list_appointments(db: Session, owner_id: int) -> list[dict]:
    appts = (
        db.query(Appointment)
        .filter(Appointment.owner_id == owner_id)
        .order_by(Appointment.scheduled_at.asc())
        .all()
    )
    return [_to_response_dict(a) for a in appts]


def get_appointment(db: Session, appointment_id: int, owner_id: int) -> Appointment:
    appt = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id, Appointment.owner_id == owner_id)
        .first()
    )
    if not appt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado.")
    return appt


def update_appointment(db: Session, appointment_id: int, data: AppointmentUpdate, owner_id: int) -> dict:
    appt = get_appointment(db, appointment_id, owner_id)

    update_data = data.model_dump(exclude_unset=True)
    # se a data/hora mudar, o lembrete deve poder disparar de novo
    if "scheduled_at" in update_data:
        appt.notified = False

    for field, value in update_data.items():
        setattr(appt, field, value)

    db.commit()
    db.refresh(appt)
    return _to_response_dict(appt)


def delete_appointment(db: Session, appointment_id: int, owner_id: int) -> None:
    appt = get_appointment(db, appointment_id, owner_id)
    db.delete(appt)
    db.commit()
