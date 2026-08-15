from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_authenticated_user, get_current_admin, get_current_user
from app.models.user import User
from app.schemas.privacy import DeleteMyAccountRequest, LegalAcceptanceRequest
from app.services.legal_service import accept_current_documents, current_legal_status
from app.services.privacy_service import cleanup_expired_security_data, export_account_data, permanently_delete_account
from app.utils.audit import audit_event

router = APIRouter(prefix="/privacy", tags=["Privacidade"])


@router.get("/legal-status")
def legal_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    return current_legal_status(db, current_user.id)


@router.post("/accept-legal")
def accept_legal(
    data: LegalAcceptanceRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    try:
        result = accept_current_documents(
            db,
            user_id=current_user.id,
            terms_accepted=data.terms_accepted,
            privacy_acknowledged=data.privacy_acknowledged,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_id=request.scope.get("vynce.request_id"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    audit_event(
        db,
        action="privacy.legal_acceptance",
        user_id=current_user.id,
        owner_id=current_user.id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_id=request.scope.get("vynce.request_id"),
        detail="current legal documents accepted",
    )
    return result


@router.get("/export-me")
def export_my_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return export_account_data(db, user=current_user)


@router.post("/delete-my-account", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    data: DeleteMyAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    permanently_delete_account(
        db,
        user=current_user,
        current_password=data.current_password,
        confirmation=data.confirmation,
    )


@router.post("/retention/cleanup")
def run_retention_cleanup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return cleanup_expired_security_data(db)
