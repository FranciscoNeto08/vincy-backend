from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ComandaItemCreate(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(ge=0, description="Preço não pode ser negativo")
    quantity: int = Field(default=1, ge=1, description="Quantidade mínima é 1")


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

    items: list[ComandaItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
