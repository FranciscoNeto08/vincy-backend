from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class ClientBase(BaseModel):
    name: str
    phone: str | None = None
    email: EmailStr | None = None
    note: str | None = None

    @field_validator("name")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("O nome do cliente não pode ficar vazio.")
        return v.strip()


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    note: str | None = None


class ClientResponse(ClientBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
