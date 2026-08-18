from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_subscriber
from app.models.user import User
from app.services.dashboard_service import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_subscriber)):
    """Retorna os indicadores principais do estabelecimento do usuário logado."""
    return get_dashboard_data(db, owner_id=current_user.id)
