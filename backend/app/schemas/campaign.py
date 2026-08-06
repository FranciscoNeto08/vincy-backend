from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CampaignCreate(BaseModel):
    channel: str  # "email" | "whatsapp"
    subject: str | None = None
    message: str
    client_ids: list[int] | None = None  # None = todos os clientes com contato válido


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
    whatsapp_links: list[WhatsAppLink] = []
