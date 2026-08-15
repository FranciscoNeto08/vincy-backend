from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    Token,
    VerifyEmailRequest,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import (
    authenticate_user,
    forgot_password,
    generate_token_for_user,
    register_user,
    resend_verification_email,
    reset_password,
    verify_email,
)
from app.utils.audit import audit_event

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _meta(request: Request) -> dict:
    return {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "request_id": request.scope.get("vynce.request_id"),
    }


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    user = register_user(
        db,
        user_data,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_id=request.scope.get("vynce.request_id"),
    )
    audit_event(db, action="auth.register", user_id=user.id, owner_id=user.id, **_meta(request))
    return user


@router.post("/login", response_model=Token)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
    except Exception:
        audit_event(db, action="auth.login", success=False, detail="login recusado", **_meta(request))
        raise

    audit_event(db, action="auth.login", user_id=user.id, owner_id=user.id, **_meta(request))
    return Token(access_token=generate_token_for_user(user))


@router.post("/verify-email", status_code=200)
def confirmar_email(data: VerifyEmailRequest, request: Request, db: Session = Depends(get_db)):
    user = verify_email(db, data.token)
    audit_event(db, action="auth.verify_email", user_id=user.id, owner_id=user.id, **_meta(request))
    return {"mensagem": "E-mail confirmado com sucesso! Já pode fazer login."}


@router.post("/resend-verification", status_code=200)
def reenviar_confirmacao(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    resend_verification_email(db, str(data.email))
    return {"mensagem": "Se aplicável, enviamos um novo link."}


@router.post("/forgot-password", status_code=200)
def esqueci_senha(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    forgot_password(db, str(data.email))
    return {"mensagem": "Se o e-mail existir na base, enviamos um link para redefinir a senha."}


@router.post("/reset-password", status_code=200)
def redefinir_senha(data: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)):
    user = reset_password(db, data.token, data.new_password)
    audit_event(db, action="auth.password_reset", user_id=user.id, owner_id=user.id, **_meta(request))
    return {"mensagem": "Senha redefinida com sucesso! Já pode fazer login."}
