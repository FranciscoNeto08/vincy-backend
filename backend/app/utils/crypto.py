from cryptography.fernet import Fernet, InvalidToken

from app.config.settings import settings


def _fernet() -> Fernet:
    if not settings.CREDENTIAL_ENCRYPTION_KEY:
        raise RuntimeError(
            "CREDENTIAL_ENCRYPTION_KEY não configurada."
        )

    try:
        return Fernet(
            settings.CREDENTIAL_ENCRYPTION_KEY.encode()
        )
    except Exception as exc:
        raise RuntimeError(
            "CREDENTIAL_ENCRYPTION_KEY inválida."
        ) from exc


def encrypt_secret(value: str) -> str:
    if not value:
        raise ValueError("Segredo vazio.")

    return _fernet().encrypt(
        value.encode("utf-8")
    ).decode("utf-8")


def decrypt_secret(value: str) -> str:
    if not value:
        raise ValueError("Segredo vazio.")

    try:
        return _fernet().decrypt(
            value.encode("utf-8")
        ).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError(
            "Não foi possível descriptografar a credencial."
        ) from exc