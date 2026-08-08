from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CampaignCreate(BaseModel):
    channel: Literal["email", "whatsapp"]
    subject: str | None = Field(default=None, max_length=200)
    message: str = Field(min_length=1, max_length=5000)
    client_ids: list[int] | None = Field(default=None, max_length=500)

    @field_validator("client_ids")
    @classmethod
    def unique_positive_ids(cls, value: list[int] | None):
        if value is None:
            return value
        if any(item <= 0 for item in value):
            raise ValueError("IDs de clientes inválidos.")
        return list(dict.fromkeys(value))


class CampaignResponse(BaseModel):
    id: int
    channel: str
    subject: str | None = None
    message: str
    total_destinatarios: int
    total_enviados: int
    total_falhas: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WhatsAppLink(BaseModel):
    client_id: int
    client_name: str
    phone: str
    link: str


class CampaignResult(BaseModel):
    campaign: CampaignResponse
    whatsapp_links: list[WhatsAppLink] = Field(default_factory=list)
