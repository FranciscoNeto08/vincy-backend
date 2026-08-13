from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.config.settings import settings
from app.models.user import User
from app.models.client import Client
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignResult
from app.services import campaign_service
from app.utils.audit import audit_event
from app.utils.rate_limit import campaign_limiter
from app.utils.unsubscribe import verify_unsubscribe_token

router = APIRouter(prefix="/campaigns", tags=["Marketing"])


@router.post("", response_model=CampaignResult, status_code=status.HTTP_201_CREATED)
def send_campaign(
    data: CampaignCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed, retry_after = campaign_limiter.hit(
        f"campaign:{current_user.id}",
        settings.CAMPAIGN_RATE_LIMIT_PER_MINUTE,
        60,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitos envios em pouco tempo. Aguarde e tente novamente.",
            headers={"Retry-After": str(retry_after)},
        )

    result = campaign_service.send_campaign(
        db,
        data,
        owner_id=current_user.id,
        sender_name=getattr(current_user, "name", None) or "Seu negócio",
        reply_to=getattr(current_user, "email", None),
    )

    audit_event(
        db,
        action="campaign.send",
        user_id=current_user.id,
        owner_id=current_user.id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_id=request.scope.get("vynce.request_id"),
        detail=(
            f"canal={data.channel}; "
            f"destinatarios={result['campaign'].total_destinatarios}"
        ),
    )
    return result


@router.get("", response_model=list[CampaignResponse])
def list_campaigns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return campaign_service.list_campaigns(db, owner_id=current_user.id)


@router.get("/unsubscribe", include_in_schema=False)
def unsubscribe(token: str, db: Session = Depends(get_db)):
    verified = verify_unsubscribe_token(token)
    if not verified:
        raise HTTPException(status_code=400, detail="Link de descadastro inválido ou expirado.")

    owner_id, client_id = verified
    client = (
        db.query(Client).filter(
            Client.id == client_id,
            Client.owner_id == owner_id,
        )
        .first()
    )
    if client:
        client.unsubscribed = True
        db.commit()

    from fastapi.responses import HTMLResponse
    return HTMLResponse(
        "<!doctype html><html lang='pt-BR'><meta charset='utf-8'>"
        "<title>Descadastro</title><body style='font-family:Arial;padding:40px'>"
        "<h2>Inscrição cancelada</h2><p>Você não receberá novas mensagens de marketing deste estabelecimento.</p>"
        "</body></html>"
    )
