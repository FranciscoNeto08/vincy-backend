from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    name: str
    price: float
    duration: int | None = None
    description: str | None = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    duration: int | None = None
    description: str | None = None
    active: bool | None = None


class ServiceResponse(ServiceBase):
    id: int
    active: bool
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
