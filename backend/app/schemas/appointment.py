from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class AppointmentCreate(BaseModel):
    client_id: int = Field(gt=0)
    service_id: int | None = Field(default=None, gt=0)
    scheduled_at: datetime
    reminder_minutes_before: int = Field(default=60, ge=0, le=10080)
    notes: str | None = Field(default=None, max_length=2000)


class AppointmentUpdate(BaseModel):
    client_id: int | None = Field(default=None, gt=0)
    service_id: int | None = Field(default=None, gt=0)
    scheduled_at: datetime | None = None
    reminder_minutes_before: int | None = Field(default=None, ge=0, le=10080)
    notes: str | None = Field(default=None, max_length=2000)
    status: Literal["agendado", "concluido", "cancelado"] | None = None
    notified: bool | None = None


class AppointmentResponse(BaseModel):
    id: int
    client_id: int
    service_id: int | None = None
    client_name: str | None = None
    service_name: str | None = None
    service_description: str | None = None
    service_duration: int | None = None
    service_price: float | None = None
    scheduled_at: datetime
    reminder_minutes_before: int
    notes: str | None = None
    status: str
    notified: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
