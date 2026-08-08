from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1)
    phone: str | None = None
    email: EmailStr | None = None


class EmployeeResponse(BaseModel):
    id: int
    name: str
    phone: str | None = None
    email: str | None = None
    active: bool
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
