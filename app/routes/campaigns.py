from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignResult
from app.services import campaign_service

router = APIRouter(prefix="/campaigns", tags=["Marketing"])


@router.post("", response_model=CampaignResult, status_code=status.HTTP_201_CREATED)
def send_campaign(
    data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return campaign_service.send_campaign(db, data, owner_id=current_user.id)


@router.get("", response_model=list[CampaignResponse])
def list_campaigns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return campaign_service.list_campaigns(db, owner_id=current_user.id)
