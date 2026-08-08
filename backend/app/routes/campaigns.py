from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.config.settings import settings
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignResult
from app.services import campaign_service
from app.utils.audit import audit_event
from app.utils.rate_limit import campaign_limiter

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

    result = campaign_service.send_campaign(db, data, owner_id=current_user.id)
    audit_event(
        db,
        action="campaign.send",
        user_id=current_user.id,
        owner_id=current_user.id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_id=request.scope.get("vynce.request_id"),
        detail=f"canal={data.channel}; destinatarios={result['campaign'].total_destinatarios}",
    )
    return result


@router.get("", response_model=list[CampaignResponse])
def list_campaigns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return campaign_service.list_campaigns(db, owner_id=current_user.id)
