from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class EmployeeCreate(BaseModel):
    name: str
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
