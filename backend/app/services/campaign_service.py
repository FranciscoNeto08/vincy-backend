import html
import re
import urllib.parse
from datetime import datetime, timezone
from sqlalchemy import func

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.campaign import Campaign
from app.models.client import Client
from app.schemas.campaign import CampaignCreate
from app.utils.email_sender import send_email_batch
from app.utils.unsubscribe import generate_unsubscribe_token

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _daily_sent_count(db: Session, owner_id: int) -> int:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    value = db.query(func.coalesce(func.sum(Campaign.total_destinatarios), 0)).filter(
        Campaign.owner_id == owner_id,
        Campaign.created_at >= start,
    ).scalar()
    return int(value or 0)


def _target_clients(
    db: Session,
    owner_id: int,
    client_ids: list[int] | None,
) -> list[Client]:
    query = db.query(Client).filter(Client.owner_id == owner_id)

    # Importante: [] significa nenhum cliente. Nunca deve virar "todos".
    if client_ids is not None:
        query = query.filter(Client.id.in_(client_ids))

    return query.limit(settings.MAX_CAMPAIGN_RECIPIENTS + 1).all()


def _valid_email(value: str | None) -> bool:
    value = str(value or "").strip()
    return len(value) <= 254 and bool(EMAIL_RE.fullmatch(value))


def _replace_name(text: str, name: str) -> str:
    return str(text or "").replace("{nome}", name or "Cliente")


def _safe_sender_name(value: str) -> str:
    return re.sub(r"[\r\n<>]", " ", str(value or "Seu negócio")).strip()[:80]


def _marketing_html(sender_name: str, subject: str, message: str, unsubscribe_url: str) -> str:
    safe_sender = html.escape(sender_name)
    safe_subject = html.escape(subject)
    safe_message = html.escape(message).replace("\n", "<br>")

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body style="margin:0;padding:0;background:#f5f5f8;font-family:Arial,Helvetica,sans-serif;color:#202027;">
        <div style="max-width:620px;margin:32px auto;background:#fff;border:1px solid #ececf2;border-radius:16px;overflow:hidden;">
            <div style="padding:24px 30px;background:#6d5dfc;color:#fff;font-size:20px;font-weight:700;">
                {safe_sender}
            </div>
            <div style="padding:30px;line-height:1.7;font-size:15px;">
                <h2 style="margin:0 0 20px;font-size:21px;color:#202027;">{safe_subject}</h2>
                <div>{safe_message}</div>
            </div>
            <div style="padding:18px 30px;background:#fafafe;border-top:1px solid #eeeef4;color:#8b8b96;font-size:11px;">
                Mensagem enviada por {safe_sender} através da Vynce.<br>
                <a href="{unsubscribe_url}" style="color:#6d5dfc;">Cancelar inscrição</a>
            </div>
        </div>
    </body>
    </html>
    """


def send_campaign(
    db: Session,
    data: CampaignCreate,
    owner_id: int,
    sender_name: str = "Seu negócio",
    reply_to: str | None = None,
) -> dict:
    clients = _target_clients(db, owner_id, data.client_ids)

    if len(clients) > settings.MAX_CAMPAIGN_RECIPIENTS:
        raise HTTPException(status_code=400, detail="Quantidade de destinatários acima do limite permitido.")
    if _daily_sent_count(db, owner_id) + len(clients) > settings.CAMPAIGN_DAILY_RECIPIENT_LIMIT:
        raise HTTPException(status_code=429, detail="Limite diário de destinatários atingido.")

    campaign = Campaign(
        channel=data.channel,
        subject=data.subject,
        message=data.message,
        owner_id=owner_id,
    )

    whatsapp_links = []

    if data.channel == "email":
        alvo = [cliente for cliente in clients if _valid_email(cliente.email) and not cliente.unsubscribed]

        if not alvo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum cliente selecionado possui e-mail válido cadastrado.",
            )

        campaign.total_destinatarios = len(alvo)
        subject_base = (data.subject or "Mensagem").strip() or "Mensagem"
        sender = _safe_sender_name(sender_name)
        payloads = []

        for cliente in alvo:
            subject = _replace_name(subject_base, cliente.name)
            message = _replace_name(data.message, cliente.name)

            token = generate_unsubscribe_token(owner_id, cliente.id)
            unsubscribe_base = settings.BACKEND_PUBLIC_URL.rstrip("/")
            unsubscribe_url = f"{unsubscribe_base}/campaigns/unsubscribe?token={urllib.parse.quote(token)}"

            payload = {
                "from": f"{sender} via Vynce <{settings.RESEND_FROM_EMAIL}>",
                "to": [cliente.email.strip()],
                "subject": subject,
                "html": _marketing_html(sender, subject, message, unsubscribe_url),
                "text": message + f"\n\nDescadastrar: {unsubscribe_url}",
                "headers": {"List-Unsubscribe": f"<{unsubscribe_url}>", "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"},
                "tags": [
                    {"name": "type", "value": "campaign"},
                    {"name": "owner", "value": str(owner_id)},
                ],
            }

            if reply_to:
                payload["reply_to"] = reply_to

            payloads.append(payload)

        try:
            campaign.total_enviados = send_email_batch(
                payloads,
                idempotency_prefix=f"campaign-{owner_id}",
            )
            campaign.total_falhas = (
                campaign.total_destinatarios - campaign.total_enviados
            )
        except Exception as exc:
            campaign.total_enviados = 0
            campaign.total_falhas = campaign.total_destinatarios
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "O serviço de e-mail não conseguiu concluir o envio. "
                    "Tente novamente em alguns instantes."
                ),
            ) from exc

    else:
        alvo = [cliente for cliente in clients if cliente.phone]

        if not alvo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum cliente selecionado possui telefone cadastrado.",
            )

        campaign.total_destinatarios = len(alvo)
        campaign.total_enviados = len(alvo)
        campaign.total_falhas = 0

        for cliente in alvo:
            message = _replace_name(data.message, cliente.name)
            numero = "".join(ch for ch in cliente.phone if ch.isdigit())

            if len(numero) in (10, 11):
                numero = "55" + numero

            whatsapp_links.append(
                {
                    "client_id": cliente.id,
                    "client_name": cliente.name,
                    "phone": cliente.phone,
                    "link": (
                        f"https://wa.me/{numero}"
                        f"?text={urllib.parse.quote(message)}"
                    ),
                }
            )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    return {
        "campaign": campaign,
        "whatsapp_links": whatsapp_links,
    }


def list_campaigns(
    db: Session,
    owner_id: int,
) -> list[Campaign]:
    return (
        db.query(Campaign)
        .filter(Campaign.owner_id == owner_id)
        .order_by(Campaign.created_at.desc())
        .all()
    )
