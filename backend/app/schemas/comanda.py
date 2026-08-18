from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ComandaItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0, le=10_000_000, allow_inf_nan=False)
    quantity: int = Field(default=1, ge=1, le=1000)


class ComandaItemResponse(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class ComandaCreate(BaseModel):
    client_id: int = Field(gt=0)
    employee_id: int = Field(gt=0)


class ComandaResponse(BaseModel):
    id: int
    client_id: int
    client_name: str | None = None
    user_id: int
    employee_id: int | None = None
    employee_name: str | None = None
    status: str
    total: float
    data_abertura: datetime
    data_fechamento: datetime | None = None
    items: list[ComandaItemResponse] = Field(default_factory=list)
    feedback_rating: int | None = None
    feedback_comment: str | None = None
    feedback_responded_at: datetime | None = None
    feedback_url: str | None = None
    model_config = ConfigDict(from_attributes=True)
