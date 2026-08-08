from pydantic import BaseModel, ConfigDict, Field


class ServiceBase(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(ge=0, description="Preço não pode ser negativo")
    duration: int | None = Field(default=None, gt=0, description="Duração em minutos, se informada, deve ser positiva")
    description: str | None = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    price: float | None = Field(default=None, ge=0)
    duration: int | None = Field(default=None, gt=0)
    description: str | None = None
    active: bool | None = None


class ServiceResponse(ServiceBase):
    id: int
    active: bool
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
