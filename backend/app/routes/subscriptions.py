from datetime import datetime, timedelta, timezone
import secrets
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.config.settings import settings
from app.models.user import User

router = APIRouter(prefix="/subscriptions", tags=["Assinaturas"])

class ActivationRequest(BaseModel):
    email: str = Field(min_length=3, max_length=150)
    days: int = Field(default=30, ge=1, le=366)

def _authorize(key: str | None):
    if not settings.SUBSCRIPTION_ADMIN_KEY or not key or not secrets.compare_digest(key, settings.SUBSCRIPTION_ADMIN_KEY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado.")

@router.post("/activate")
def activate(data: ActivationRequest, x_vynce_admin_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    _authorize(x_vynce_admin_key)
    user=db.query(User).filter(User.email==data.email.strip().lower()).first()
    if not user: raise HTTPException(status_code=404, detail="Conta não encontrada.")
    now=datetime.now(timezone.utc)
    base=user.subscription_expires_at if user.subscription_expires_at and user.subscription_expires_at > now else now
    user.subscription_status="active"; user.subscription_activated_at=now; user.subscription_expires_at=base+timedelta(days=data.days)
    db.commit(); return {"status":"active","email":user.email,"expires_at":user.subscription_expires_at}

@router.post("/block")
def block(data: ActivationRequest, x_vynce_admin_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    _authorize(x_vynce_admin_key)
    user=db.query(User).filter(User.email==data.email.strip().lower()).first()
    if not user: raise HTTPException(status_code=404, detail="Conta não encontrada.")
    user.subscription_status="blocked"; db.commit(); return {"status":"blocked","email":user.email}
