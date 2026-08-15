from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


PermissionSource = Literal["not_informed", "presencial", "formulario", "importacao", "outro"]


class ClientBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("name")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("O nome do cliente não pode ficar vazio.")
        return v


class ClientCreate(ClientBase):
    email_marketing_opt_in: bool = False
    whatsapp_marketing_opt_in: bool = False
    marketing_permission_source: PermissionSource = "not_informed"
    marketing_legal_basis_note: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_marketing_permission(self):
        if (self.email_marketing_opt_in or self.whatsapp_marketing_opt_in) and self.marketing_permission_source == "not_informed":
            raise ValueError("Informe a origem da permissão de marketing.")
        if self.marketing_permission_source == "outro" and not (self.marketing_legal_basis_note or "").strip():
            raise ValueError("Descreva a origem/base legal quando selecionar 'Outro'.")
        return self


class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    note: str | None = Field(default=None, max_length=2000)
    email_marketing_opt_in: bool | None = None
    whatsapp_marketing_opt_in: bool | None = None
    marketing_permission_source: PermissionSource | None = None
    marketing_legal_basis_note: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_marketing_permission(self):
        enabling = self.email_marketing_opt_in is True or self.whatsapp_marketing_opt_in is True
        if enabling and (self.marketing_permission_source is None or self.marketing_permission_source == "not_informed"):
            raise ValueError("Informe a origem da permissão de marketing.")
        if self.marketing_permission_source == "outro" and not (self.marketing_legal_basis_note or "").strip():
            raise ValueError("Descreva a origem/base legal quando selecionar 'Outro'.")
        return self


class ClientResponse(ClientBase):
    id: int
    owner_id: int
    created_at: datetime
    email_marketing_allowed: bool = False
    whatsapp_marketing_allowed: bool = False
    marketing_permission_source: str = "not_informed"
    marketing_legal_basis_note: str | None = None

    model_config = ConfigDict(from_attributes=True)
