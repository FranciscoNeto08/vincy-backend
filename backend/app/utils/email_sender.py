import requests

from app.config.settings import settings


def send_email(to_email: str, subject: str, html: str) -> None:
    """Envia um e-mail via API do Resend. LanÃ§a RuntimeError se falhar ou nÃ£o configurado."""

    if not settings.RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY nÃ£o configurada no servidor.")

    if not settings.RESEND_FROM_EMAIL:
        raise RuntimeError("RESEND_FROM_EMAIL nÃ£o configurado no servidor.")

    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "from": f"Vynce <{settings.RESEND_FROM_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=20)

    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"Erro ao enviar e-mail pelo Resend: {detail}")


def base_email_html(title: str, body_html: str) -> str:
    """Template simples e consistente para os e-mails transacionais do sistema."""
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#f6f6f9;font-family:Arial, Helvetica, sans-serif;color:#202027;">
        <div style="max-width:620px;margin:40px auto;background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #ececf2;">
            <div style="background:#6d5dfc;padding:24px 32px;color:#ffffff;">
                <h2 style="margin:0;font-size:22px;">Vynce</h2>
            </div>
            <div style="padding:32px;line-height:1.7;font-size:15px;">
                <h3 style="margin-top:0;margin-bottom:20px;color:#202027;">{title}</h3>
                {body_html}
            </div>
            <div style="padding:20px 32px;background:#fafafe;color:#8b8b96;font-size:12px;border-top:1px solid #eeeeF4;">
                Enviado atravÃ©s da Vynce.
            </div>
        </div>
    </body>
    </html>
    """

