from pydantic import BaseModel, ConfigDict, Field


class ServiceBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0, le=10_000_000, allow_inf_nan=False)
    duration: int | None = Field(default=None, gt=0, le=24 * 60)
    description: str | None = Field(default=None, max_length=2000)


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, ge=0, le=10_000_000, allow_inf_nan=False)
    duration: int | None = Field(default=None, gt=0, le=24 * 60)
    description: str | None = Field(default=None, max_length=2000)
    active: bool | None = None


class ServiceResponse(ServiceBase):
    id: int
    active: bool
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
