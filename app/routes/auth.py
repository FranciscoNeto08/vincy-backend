from fastapi import APIRouter, Depends
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

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Cadastra um novo usuário no sistema e envia e-mail de confirmação."""
    return register_user(db, user_data)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login via OAuth2 (username = e-mail).
    Retorna um token JWT para ser usado em 'Authorization: Bearer <token>'.
    Exige e-mail confirmado e aplica bloqueio temporário após tentativas incorretas.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    token = generate_token_for_user(user)
    return Token(access_token=token)


@router.post("/verify-email", status_code=200)
def confirmar_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Confirma o e-mail do usuário a partir do token recebido por e-mail."""
    verify_email(db, data.token)
    return {"mensagem": "E-mail confirmado com sucesso! Já pode fazer login."}


@router.post("/resend-verification", status_code=200)
def reenviar_confirmacao(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Reenvia o e-mail de confirmação de cadastro, se aplicável."""
    resend_verification_email(db, data.email)
    return {"mensagem": "Se o e-mail existir e ainda não estiver confirmado, enviamos um novo link."}


@router.post("/forgot-password", status_code=200)
def esqueci_senha(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Envia um link de redefinição de senha para o e-mail informado."""
    forgot_password(db, data.email)
    return {"mensagem": "Se o e-mail existir na base, enviamos um link para redefinir a senha."}


@router.post("/reset-password", status_code=200)
def redefinir_senha(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Define uma nova senha a partir do token recebido por e-mail."""
    reset_password(db, data.token, data.new_password)
    return {"mensagem": "Senha redefinida com sucesso! Já pode fazer login."}
