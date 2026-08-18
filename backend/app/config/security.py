import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.settings import settings

# Novas senhas usam Argon2. Bcrypt é mantido SOMENTE para validar hashes antigos
# e migrá-los automaticamente após o próximo login bem-sucedido.
password_hash = PasswordHash.recommended()
legacy_bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    valid, _ = verify_and_upgrade_password(plain_password, hashed_password)
    return valid


def verify_and_upgrade_password(plain_password: str, hashed_password: str) -> tuple[bool, str | None]:
    """Valida Argon2 e migra bcrypt legado sem obrigar o usuário a trocar a senha."""
    try:
        return password_hash.verify_and_update(plain_password, hashed_password)
    except UnknownHashError:
        try:
            valid = legacy_bcrypt.verify(plain_password, hashed_password)
        except Exception:
            return False, None
        if not valid:
            return False, None
        return True, hash_password(plain_password)


def create_access_token(user_id: int, token_version: int) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "ver": int(token_version or 0),
        "iat": int(now.timestamp()),
        "exp": expire,
        "jti": secrets.token_urlsafe(18),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require_exp": True, "require_sub": True},
        )
    except JWTError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.models.user import User

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    token_version = payload.get("ver")

    try:
        user_id_int = int(user_id)
        token_version_int = int(token_version)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id_int).first()

    if user is None or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Permite invalidar todos os tokens antigos após troca/reset de senha.
    if token_version_int != int(user.token_version or 0):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_admin(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )
    return current_user


def get_current_subscriber(current_user=Depends(get_current_user)):
    """Bloqueia recursos pagos no backend; blur no frontend é apenas UX."""
    now = datetime.now(timezone.utc)
    expires = current_user.subscription_expires_at
    if expires is not None and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if current_user.subscription_status != "active" or (expires is not None and expires <= now):
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Acesso aguardando liberação comercial. Entre em contato com a Vynce para contratar ou renovar.")
    return current_user
