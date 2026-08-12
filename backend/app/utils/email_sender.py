import re
import uuid

import requests

from app.config.settings import settings


def _safe_name(value: str | None) -> str:
    value = re.sub(r"[\r\n<>]", " ", str(value or "Vynce")).strip()
    return value[:80] or "Vynce"


def _headers(idempotency_key: str | None = None) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key[:256]
    return headers


def _ensure_configured() -> None:
    if not settings.RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY não configurada no servidor.")
    if not settings.RESEND_FROM_EMAIL:
        raise RuntimeError("RESEND_FROM_EMAIL não configurado no servidor.")


def send_email(
    to_email: str,
    subject: str,
    html: str,
    *,
    from_name: str = "Vynce",
    reply_to: str | None = None,
) -> None:
    """Envia um e-mail individual sem quebrar os fluxos transacionais existentes."""
    _ensure_configured()

    payload = {
        "from": f"{_safe_name(from_name)} <{settings.RESEND_FROM_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html,
    }
    if reply_to:
        payload["reply_to"] = reply_to

    response = requests.post(
        "https://api.resend.com/emails",
        headers=_headers(str(uuid.uuid4())),
        json=payload,
        timeout=20,
    )

    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"Erro ao enviar e-mail pelo Resend: {detail}")


def send_email_batch(
    emails: list[dict],
    *,
    idempotency_prefix: str = "campaign",
) -> int:
    """Envia em lotes de no máximo 100 mensagens por chamada ao Resend."""
    _ensure_configured()

    if not emails:
        return 0

    total = 0

    for index in range(0, len(emails), 100):
        chunk = emails[index : index + 100]

        response = requests.post(
            "https://api.resend.com/emails/batch",
            headers=_headers(
                f"{idempotency_prefix}-{index // 100}-{uuid.uuid4().hex}"
            ),
            json=chunk,
            timeout=30,
        )

        if not response.ok:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise RuntimeError(f"Erro ao enviar lote pelo Resend: {detail}")

        total += len(chunk)

    return total


def base_email_html(title: str, body_html: str) -> str:
    """Template dos e-mails transacionais da Vynce."""
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#f6f6f9;font-family:Arial,Helvetica,sans-serif;color:#202027;">
        <div style="max-width:620px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;border:1px solid #ececf2;">
            <div style="background:#6d5dfc;padding:24px 32px;color:#fff;">
                <h2 style="margin:0;font-size:22px;">Vynce</h2>
            </div>
            <div style="padding:32px;line-height:1.7;font-size:15px;">
                <h3 style="margin-top:0;margin-bottom:20px;color:#202027;">{title}</h3>
                {body_html}
            </div>
            <div style="padding:20px 32px;background:#fafafe;color:#8b8b96;font-size:12px;border-top:1px solid #eeeef4;">
                Enviado através da Vynce.
            </div>
        </div>
    </body>
    </html>
    """
