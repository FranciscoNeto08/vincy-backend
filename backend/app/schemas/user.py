from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    theme: str | None = None
    password: str | None = None
    current_password: str | None = None
    role: str | None = None
    active: bool | None = None


class UserResponse(UserBase):
    id: int
    theme: str
    role: str
    active: bool

    model_config = ConfigDict(from_attributes=True)