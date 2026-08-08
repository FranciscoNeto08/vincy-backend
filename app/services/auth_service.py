import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.security import create_access_token, hash_password, verify_password
from app.config.settings import settings
from app.models.email_token import EmailToken
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.email_sender import base_email_html, send_email


TOKEN_EXPIRE_HOURS_VERIFY = 48
TOKEN_EXPIRE_HOURS_RESET = 2


def _now():
    return datetime.now(timezone.utc)


def _generate_token(db: Session, user_id: int, kind: str, expire_hours: int) -> str:
    token = secrets.token_urlsafe(32)

    db.add(
        EmailToken(
            user_id=user_id,
            token=token,
            kind=kind,
            expires_at=_now() + timedelta(hours=expire_hours),
        )
    )
    db.commit()
    return token


def _consume_token(db: Session, token: str, kind: str) -> EmailToken:
    registro = (
        db.query(EmailToken)
        .filter(EmailToken.token == token, EmailToken.kind == kind)
        .first()
    )

    if not registro or registro.used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link inválido ou já utilizado.")

    expires_at = registro.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < _now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link expirado. Solicite um novo.")

    registro.used = True
    db.commit()

    return registro


def _send_verification_email(db: Session, user: User) -> None:
    token = _generate_token(db, user.id, "verify_email", TOKEN_EXPIRE_HOURS_VERIFY)
    link = f"{settings.FRONTEND_URL}/index.html?verify_token={token}"

    html = base_email_html(
        "Confirme seu e-mail",
        f'''
        <p>Olá, {user.name}! Falta pouco para começar a usar a Vincy.</p>
        <p>Clique no botão abaixo para confirmar seu e-mail (válido por {TOKEN_EXPIRE_HOURS_VERIFY} horas):</p>
        <p style="margin:24px 0;">
            <a href="{link}" style="background:#6d5dfc;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">Confirmar e-mail</a>
        </p>
        <p>Se o botão não funcionar, copie e cole este link: {link}</p>
        ''',
    )

    try:
        send_email(user.email, "Confirme seu e-mail — Vincy", html)
    except RuntimeError as erro:
        print(f"[aviso] Não foi possível enviar e-mail de confirmação para {user.email}: {erro}")


def _send_security_alert_email(user: User) -> None:
    html = base_email_html(
        "Alerta de segurança",
        f'''
        <p>Detectamos várias tentativas de login malsucedidas na sua conta ({user.email}).</p>
        <p>Por segurança, o acesso foi bloqueado temporariamente por {settings.LOGIN_LOCK_MINUTES} minutos.</p>
        <p>Se não foi você, recomendamos trocar sua senha assim que possível.</p>
        ''',
    )

    try:
        send_email(user.email, "Alerta de segurança — Vincy", html)
    except RuntimeError as erro:
        print(f"[aviso] Não foi possível enviar alerta de segurança para {user.email}: {erro}")


def register_user(db: Session, user_data: UserCreate) -> User:
    """Cria um novo usuário, garantindo que o e-mail seja único, e envia e-mail de confirmação."""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário cadastrado com esse e-mail.",
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password=hash_password(user_data.password),
        email_verified=not settings.REQUIRE_EMAIL_VERIFICATION,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    if settings.REQUIRE_EMAIL_VERIFICATION:
        _send_verification_email(db, user)

    return user


def verify_email(db: Session, token: str) -> None:
    registro = _consume_token(db, token, "verify_email")

    user = db.query(User).filter(User.id == registro.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    user.email_verified = True
    db.commit()


def resend_verification_email(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()

    # Não revela se o e-mail existe ou não — evita enumeração de contas.
    if not user or user.email_verified:
        return

    _send_verification_email(db, user)


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Valida e-mail/senha, aplica bloqueio por tentativas e exige e-mail confirmado."""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    # Verifica se a conta está temporariamente bloqueada.
    if user.locked_until:
        locked_until = user.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)

        if locked_until > _now():
            minutos_restantes = max(1, int((locked_until - _now()).total_seconds() // 60) + 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Conta temporariamente bloqueada por excesso de tentativas. Tente novamente em {minutos_restantes} minuto(s).",
            )

    if not verify_password(password, user.password):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

        if user.failed_login_attempts >= settings.LOGIN_MAX_ATTEMPTS:
            user.locked_until = _now() + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
            user.failed_login_attempts = 0
            db.commit()
            _send_security_alert_email(user)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Muitas tentativas incorretas. Conta bloqueada por {settings.LOGIN_LOCK_MINUTES} minutos.",
            )

        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Contate um administrador.",
        )

    if settings.REQUIRE_EMAIL_VERIFICATION and not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Confirme seu e-mail antes de entrar. Verifique sua caixa de entrada.",
        )

    # Login bem-sucedido: zera o contador de tentativas.
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    return user


def forgot_password(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()

    # Não revela se o e-mail existe ou não — evita enumeração de contas.
    if not user:
        return

    token = _generate_token(db, user.id, "reset_password", TOKEN_EXPIRE_HOURS_RESET)
    link = f"{settings.FRONTEND_URL}/index.html?reset_token={token}"

    html = base_email_html(
        "Redefinir senha",
        f'''
        <p>Recebemos uma solicitação para redefinir a senha da sua conta ({user.email}).</p>
        <p>Clique no botão abaixo para criar uma nova senha (válido por {TOKEN_EXPIRE_HOURS_RESET} horas):</p>
        <p style="margin:24px 0;">
            <a href="{link}" style="background:#6d5dfc;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">Criar nova senha</a>
        </p>
        <p>Se você não solicitou isso, ignore este e-mail — sua senha atual continua a mesma.</p>
        ''',
    )

    try:
        send_email(user.email, "Redefinir senha — Vincy", html)
    except RuntimeError as erro:
        print(f"[aviso] Não foi possível enviar e-mail de redefinição para {user.email}: {erro}")


def reset_password(db: Session, token: str, new_password: str) -> None:
    registro = _consume_token(db, token, "reset_password")

    user = db.query(User).filter(User.id == registro.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    user.password = hash_password(new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()


def generate_token_for_user(user: User) -> str:
    return create_access_token(data={"sub": str(user.id)})
