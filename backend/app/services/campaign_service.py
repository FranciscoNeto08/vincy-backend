import urllib.parse
import requests

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.campaign import Campaign
from app.models.client import Client
from app.schemas.campaign import CampaignCreate


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

    if not settings.RESEND_API_KEY:
        raise RuntimeError(
            "RESEND_API_KEY não configurada no servidor."
        )

    if not settings.RESEND_FROM_EMAIL:
        raise RuntimeError(
            "RESEND_FROM_EMAIL não configurado no servidor."
        )

    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
    </head>

    <body
        style="
            margin:0;
            padding:0;
            background:#f6f6f9;
            font-family:Arial, Helvetica, sans-serif;
            color:#202027;
        "
    >

        <div
            style="
                max-width:620px;
                margin:40px auto;
                background:#ffffff;
                border-radius:16px;
                overflow:hidden;
                border:1px solid #ececf2;
            "
        >

            <div
                style="
                    background:#6d5dfc;
                    padding:24px 32px;
                    color:#ffffff;
                "
            >

                <h2
                    style="
                        margin:0;
                        font-size:22px;
                    "
                >
                    Vincy
                </h2>

            </div>

            <div
                style="
                    padding:32px;
                    line-height:1.7;
                    font-size:15px;
                "
            >

                <h3
                    style="
                        margin-top:0;
                        margin-bottom:20px;
                        color:#202027;
                    "
                >
                    {subject or "Mensagem"}
                </h3>

                <div
                    style="
                        white-space:pre-line;
                    "
                >
                    {message}
                </div>

            </div>

            <div
                style="
                    padding:20px 32px;
                    background:#fafafe;
                    color:#8b8b96;
                    font-size:12px;
                    border-top:1px solid #eeeeF4;
                "
            >

                Enviado através da Vincy.

            </div>

        </div>

    </body>
    </html>
    """

    payload = {
        "from": f"Vincy <{settings.RESEND_FROM_EMAIL}>",
        "to": [to_email],
        "subject": subject or "Mensagem",
        "html": html
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=20
    )

    if not response.ok:

        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"Erro ao enviar e-mail pelo Resend: {detail}"
        )


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