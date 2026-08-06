from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None
    active: bool | None = None


class UserResponse(UserBase):
    id: int
    role: str
    active: bool

    model_config = ConfigDict(from_attributes=True)