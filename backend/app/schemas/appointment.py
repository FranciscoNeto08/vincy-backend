from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppointmentCreate(BaseModel):
    client_id: int
    service_id: int | None = None
    scheduled_at: datetime
    reminder_minutes_before: int = 60
    notes: str | None = None


class AppointmentUpdate(BaseModel):
    client_id: int | None = None
    service_id: int | None = None
    scheduled_at: datetime | None = None
    reminder_minutes_before: int | None = None
    notes: str | None = None
    status: str | None = None
    notified: bool | None = None


class AppointmentResponse(BaseModel):
    id: int
    client_id: int
    service_id: int | None = None
    client_name: str | None = None
    service_name: str | None = None
    scheduled_at: datetime
    reminder_minutes_before: int
    notes: str | None = None
    status: str
    notified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
