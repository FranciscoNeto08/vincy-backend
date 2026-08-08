from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    theme: str | None = None
    password: str | None = None
    current_password: str | None = None
    role: str | None = None
    active: bool | None = None

    @field_validator("password")
    @classmethod
    def senha_minima(cls, v: str | None) -> str | None:
        if v is not None and len(v) < 6:
            raise ValueError("A senha precisa ter pelo menos 6 caracteres.")
        return v


class UserResponse(UserBase):
    id: int
    theme: str
    role: str
    active: bool

    model_config = ConfigDict(from_attributes=True)