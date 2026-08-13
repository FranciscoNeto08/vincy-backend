# app/schemas/evolution.py
import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field, field_validator


class EvolutionConfigCreate(BaseModel):
    api_key: str = Field(min_length=8, max_length=255)
    base_url: HttpUrl
    instance_name: str | None = Field(default="default", min_length=1, max_length=100)

    @field_validator("instance_name")
    @classmethod
    def clean_instance(cls, value: str | None):
        if value is None:
            return "default"
        value = value.strip()
        if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
            raise ValueError("Nome de instância inválido.")
        return value


class EvolutionConfigResponse(BaseModel):
    id: int
    base_url: str
    instance_name: str
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def api_key_masked(self) -> str:
        # A API key nunca é devolvida pelo backend.
        return "********"


class WhatsAppMessageSend(BaseModel):
    phone: str = Field(min_length=10, max_length=20)
    message: str = Field(min_length=1, max_length=500)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) not in {10, 11, 12, 13}:
            raise ValueError("Número de telefone inválido.")
        return value.strip()


class WhatsAppMessageResponse(BaseModel):
    success: bool
    phone: str | None = None
    message_id: str | None = None
    error: str | None = None


class WhatsAppCampaignRequest(BaseModel):
    client_ids: list[int] | None = Field(default=None, max_length=500)
    subject: str = Field(default="Mensagem", max_length=200)
    message: str = Field(min_length=1, max_length=500)
    send_via_api: bool = False

    @field_validator("client_ids")
    @classmethod
    def unique_ids(cls, value):
        if value is None:
            return value
        if any(item <= 0 for item in value):
            raise ValueError("IDs inválidos.")
        return list(dict.fromkeys(value))


class EvolutionTestConnection(BaseModel):
    success: bool
    connected: bool | None = None
    instance_status: str | None = None
    error: str | None = None
