import urllib.parse
import requests

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.campaign import Campaign
from app.models.client import Client
from app.schemas.campaign import CampaignCreate
from app.utils.email_sender import base_email_html, send_email


def _target_clients(
    db: Session,
    owner_id: int,
    client_ids: list[int] | None
) -> list[Client]:

    query = db.query(Client).filter(
        Client.owner_id == owner_id
    )

    if client_ids:
        query = query.filter(
            Client.id.in_(client_ids)
        )

    return query.all()


def _send_email(
    to_email: str,
    subject: str,
    message: str
) -> None:

    html = base_email_html(
        subject or "Mensagem",
        f'<div style="white-space:pre-line;">{message}</div>'
    )

    send_email(to_email, subject or "Mensagem", html)


def send_campaign(
    db: Session,
    data: CampaignCreate,
    owner_id: int
) -> dict:

    if data.channel not in (
        "email",
        "whatsapp"
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Canal inválido."
        )


    clients = _target_clients(
        db,
        owner_id,
        data.client_ids
    )


    campaign = Campaign(
        channel=data.channel,
        subject=data.subject,
        message=data.message,
        owner_id=owner_id
    )


    whatsapp_links = []


    # =====================================================
    # E-MAIL
    # =====================================================

    if data.channel == "email":

        alvo = [
            cliente
            for cliente in clients
            if cliente.email
        ]

        campaign.total_destinatarios = len(alvo)

        enviados = 0
        falhas = 0


        for cliente in alvo:

            try:

                _send_email(
                    cliente.email,
                    data.subject or "Mensagem",
                    data.message
                )

                enviados += 1

            except Exception as erro:

                print(
                    f"Erro ao enviar e-mail para "
                    f"{cliente.email}: {erro}"
                )

                falhas += 1


        campaign.total_enviados = enviados
        campaign.total_falhas = falhas


    # =====================================================
    # WHATSAPP
    # =====================================================

    else:

        alvo = [
            cliente
            for cliente in clients
            if cliente.phone
        ]


        campaign.total_destinatarios = len(alvo)

        campaign.total_enviados = len(alvo)

        campaign.total_falhas = 0


        texto_codificado = urllib.parse.quote(
            data.message
        )


        for cliente in alvo:

            numero = "".join(
                caractere
                for caractere in cliente.phone
                if caractere.isdigit()
            )


            # Adiciona código do Brasil caso o número tenha
            # apenas DDD + telefone.
            if len(numero) in (10, 11):
                numero = "55" + numero


            whatsapp_links.append(
                {
                    "client_id": cliente.id,
                    "client_name": cliente.name,
                    "phone": cliente.phone,
                    "link":
                        f"https://wa.me/{numero}"
                        f"?text={texto_codificado}"
                }
            )


    # =====================================================
    # SALVA CAMPANHA
    # =====================================================

    db.add(campaign)

    db.commit()

    db.refresh(campaign)


    return {
        "campaign": campaign,
        "whatsapp_links": whatsapp_links
    }


def list_campaigns(
    db: Session,
    owner_id: int
) -> list[Campaign]:

    return (
        db.query(Campaign)
        .filter(
            Campaign.owner_id == owner_id
        )
        .order_by(
            Campaign.created_at.desc()
        )
        .all()
    )