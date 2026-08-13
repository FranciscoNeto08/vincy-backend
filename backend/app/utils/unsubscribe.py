"""Tokens de descadastro sem necessidade de tabela adicional."""
from __future__ import annotations

import base64
import hashlib
import hmac

from app.config.settings import settings


def _secret() -> bytes:
    if len(settings.SECRET_KEY) < 32:
        raise RuntimeError("SECRET_KEY insegura para tokens de descadastro.")
    return settings.SECRET_KEY.encode()


def generate_unsubscribe_token(owner_id: int, client_id: int) -> str:
    payload = f"{owner_id}:{client_id}".encode()
    signature = hmac.new(_secret(), payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(payload + b"." + signature).decode().rstrip("=")


def verify_unsubscribe_token(token: str) -> tuple[int, int] | None:
    try:
        padded = token + "=" * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(padded.encode())
        payload, signature = raw.rsplit(b".", 1)
        expected = hmac.new(_secret(), payload, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            return None
        owner_raw, client_raw = payload.decode().split(":", 1)
        owner_id, client_id = int(owner_raw), int(client_raw)
        if owner_id <= 0 or client_id <= 0:
            return None
        return owner_id, client_id
    except (ValueError, TypeError, UnicodeDecodeError, base64.binascii.Error):
        return None
