from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip()


class UserCreate(UserBase):
    password: str = Field(min_length=15, max_length=128)
    terms_accepted: bool = False
    privacy_acknowledged: bool = False

    @model_validator(mode="after")
    def require_legal_confirmation(self):
        if self.terms_accepted is not True or self.privacy_acknowledged is not True:
            raise ValueError("É necessário aceitar os documentos legais vigentes.")
        return self


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    theme: Literal["claro", "escuro"] | None = None
    password: str | None = Field(default=None, min_length=15, max_length=128)
    current_password: str | None = Field(default=None, max_length=128)
    role: Literal["admin", "funcionario"] | None = None
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def clean_optional_name(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None


class UserResponse(UserBase):
    id: int
    theme: str
    role: str
    active: bool

    model_config = ConfigDict(from_attributes=True)
