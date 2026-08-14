import hashlib
import html
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.security import (
    create_access_token,
    hash_password,
    verify_and_upgrade_password,
)
from app.config.settings import settings
from app.models.email_token import EmailToken
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.email_sender import base_email_html, send_email

TOKEN_EXPIRE_HOURS_VERIFY = 24
TOKEN_EXPIRE_MINUTES_RESET = 30

# Equaliza parte do custo de logins para e-mails inexistentes e dificulta
# enumeração por análise de tempo.
_DUMMY_PASSWORD_HASH = hash_password("vynce-dummy-password-never-used")


def _now():
    return datetime.now(timezone.utc)


def _token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _generate_token(db: Session, user_id: int, kind: str, expires_at: datetime) -> str:
    # Invalida tokens anteriores do mesmo tipo para reduzir janela de abuso.
    db.query(EmailToken).filter(
        EmailToken.user_id == user_id,
        EmailToken.kind == kind,
        EmailToken.used.is_(False),
    ).update({EmailToken.used: True}, synchronize_session=False)

    plain_token = secrets.token_urlsafe(32)
    db.add(
        EmailToken(
            user_id=user_id,
            token=_token_digest(plain_token),
            kind=kind,
            expires_at=expires_at,
        )
    )
    db.commit()
    return plain_token


def _consume_token(db: Session, token: str, kind: str) -> EmailToken:
    if not token or len(token) > 256:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link inválido ou expirado.")

    digest = _token_digest(token)
    registro = (
        db.query(EmailToken)
        .filter(
            EmailToken.kind == kind,
            EmailToken.used.is_(False),
            # Compatibilidade temporária com tokens antigos armazenados em texto puro.
            (EmailToken.token == digest) | (EmailToken.token == token),
        )
        .first()
    )

    if not registro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link inválido ou expirado.")

    expires_at = registro.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < _now():
        registro.used = True
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link inválido ou expirado.")

    # Uso único. Marcamos antes de executar a ação sensível.
    registro.used = True
    db.commit()
    return registro


def _send_verification_email(db: Session, user: User) -> None:
    token = _generate_token(
        db,
        user.id,
        "verify_email",
        _now() + timedelta(hours=TOKEN_EXPIRE_HOURS_VERIFY),
    )
    link = f"{settings.FRONTEND_URL.rstrip('/')}/index.html?verify_token={token}"

    html = base_email_html(
        "Confirme seu e-mail",
        f'''
        <p>Olá, {html.escape(user.name)}! Falta pouco para começar a usar o Vynce.</p>
        <p>Clique no botão abaixo para confirmar seu e-mail. O link é de uso único e expira em {TOKEN_EXPIRE_HOURS_VERIFY} horas.</p>
        <p style="margin:24px 0;">
            <a href="{link}" style="background:#6d5dfc;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">Confirmar e-mail</a>
        </p>
        ''',
    )
    send_email(user.email, "Confirme seu e-mail — Vynce", html)


def _send_security_alert_email(user: User) -> None:
    html = base_email_html(
        "Alerta de segurança",
        f'''
        <p>Detectamos várias tentativas de login malsucedidas na sua conta.</p>
        <p>Por segurança, o acesso foi bloqueado temporariamente por {settings.LOGIN_LOCK_MINUTES} minutos.</p>
        <p>Se não foi você, recomendamos redefinir sua senha.</p>
        ''',
    )
    try:
        send_email(user.email, "Alerta de segurança — Vynce", html)
    except Exception:
        # Não expõe detalhes do provedor e não interrompe o bloqueio da conta.
        pass


def register_user(db: Session, user_data: UserCreate) -> User:
    email = str(user_data.email).strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar a conta com os dados informados.",
        )

    user = User(
        name=user_data.name.strip(),
        email=email,
        phone=user_data.phone,
        password=hash_password(user_data.password),
        email_verified=not settings.REQUIRE_EMAIL_VERIFICATION,
        token_version=0,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    if settings.REQUIRE_EMAIL_VERIFICATION:
        try:
            _send_verification_email(db, user)
        except Exception:
            # Cadastro já foi concluído. O usuário pode pedir reenvio.
            pass

    return user


def verify_email(db: Session, token: str) -> User:
    registro = _consume_token(db, token, "verify_email")
    user = db.query(User).filter(User.id == registro.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link inválido ou expirado.")
    user.email_verified = True
    db.commit()
    return user


def resend_verification_email(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    # Resposta externa é sempre genérica.
    if not user or user.email_verified:
        return
    try:
        _send_verification_email(db, user)
    except Exception:
        pass


def authenticate_user(db: Session, email: str, password: str) -> User:
    normalized_email = email.strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()

    if not user:
        # Executa hash verification para reduzir diferença temporal.
        verify_and_upgrade_password(password, _DUMMY_PASSWORD_HASH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    if user.locked_until:
        locked_until = user.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
        if locked_until > _now():
            retry_after = max(1, int((locked_until - _now()).total_seconds()))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas tentativas. Aguarde antes de tentar novamente.",
                headers={"Retry-After": str(retry_after)},
            )

    valid, upgraded_hash = verify_and_upgrade_password(password, user.password)

    if not valid:
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= settings.LOGIN_MAX_ATTEMPTS:
            user.locked_until = _now() + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
            user.failed_login_attempts = 0
            db.commit()
            _send_security_alert_email(user)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas tentativas. Aguarde antes de tentar novamente.",
                headers={"Retry-After": str(settings.LOGIN_LOCK_MINUTES * 60)},
            )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    if not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conta indisponível.")

    if settings.REQUIRE_EMAIL_VERIFICATION and not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Confirme seu e-mail antes de entrar. Verifique sua caixa de entrada.",
        )

    if upgraded_hash:
        user.password = upgraded_hash
        user.password_changed_at = _now()

    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    return user


def forgot_password(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or not user.active:
        return

    token = _generate_token(
        db,
        user.id,
        "reset_password",
        _now() + timedelta(minutes=TOKEN_EXPIRE_MINUTES_RESET),
    )
    link = f"{settings.FRONTEND_URL.rstrip('/')}/index.html?reset_token={token}"

    html = base_email_html(
        "Redefinir senha",
        f'''
        <p>Recebemos uma solicitação para redefinir sua senha.</p>
        <p>O link abaixo é de uso único e expira em {TOKEN_EXPIRE_MINUTES_RESET} minutos.</p>
        <p style="margin:24px 0;">
            <a href="{link}" style="background:#6d5dfc;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">Criar nova senha</a>
        </p>
        <p>Se você não solicitou isso, ignore este e-mail.</p>
        ''',
    )
    try:
        send_email(user.email, "Redefinir senha — Vynce", html)
    except Exception:
        pass


def reset_password(db: Session, token: str, new_password: str) -> User:
    registro = _consume_token(db, token, "reset_password")
    user = db.query(User).filter(User.id == registro.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link inválido ou expirado.")

    user.password = hash_password(new_password)
    user.password_changed_at = _now()
    user.token_version = int(user.token_version or 0) + 1
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    # Invalida outros links pendentes de reset.
    db.query(EmailToken).filter(
        EmailToken.user_id == user.id,
        EmailToken.kind == "reset_password",
        EmailToken.used.is_(False),
    ).update({EmailToken.used: True}, synchronize_session=False)
    db.commit()
    return user


def generate_token_for_user(user: User) -> str:
    return create_access_token(user.id, int(user.token_version or 0))


def send_new_verification_after_email_change(db: Session, user: User) -> None:
    if settings.REQUIRE_EMAIL_VERIFICATION:
        try:
            _send_verification_email(db, user)
        except Exception:
            pass
