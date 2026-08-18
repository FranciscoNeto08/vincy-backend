from datetime import datetime, timedelta, timezone
from html import escape
import secrets

from fastapi import APIRouter, Depends, Form, Header, HTTPException, status
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.config.settings import settings
from app.models.user import User
from app.utils.email_sender import base_email_html, send_email

router = APIRouter(prefix="/subscriptions", tags=["Assinaturas"])

_APPROVAL_AUDIENCE = "vynce-subscription-approval"
_APPROVAL_PURPOSE = "subscription_approval"


class ActivationRequest(BaseModel):
    email: str = Field(min_length=3, max_length=150)
    days: int = Field(default=30, ge=1, le=366)


def _authorize(key: str | None):
    if (
        not settings.SUBSCRIPTION_ADMIN_KEY
        or not key
        or not secrets.compare_digest(key, settings.SUBSCRIPTION_ADMIN_KEY)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado.")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _approval_token(user: User) -> str:
    now = _now()
    payload = {
        "sub": str(user.id),
        "purpose": _APPROVAL_PURPOSE,
        "email": user.email,
        "iat": int(now.timestamp()),
        "exp": now + timedelta(hours=settings.SUBSCRIPTION_APPROVAL_TOKEN_HOURS),
        "jti": secrets.token_urlsafe(18),
        "iss": settings.JWT_ISSUER,
        "aud": _APPROVAL_AUDIENCE,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _decode_approval_token(token: str) -> dict:
    if not token or len(token) > 4096:
        raise HTTPException(status_code=400, detail="Solicitação inválida ou expirada.")
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=_APPROVAL_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require_exp": True, "require_sub": True},
        )
    except JWTError as exc:
        raise HTTPException(status_code=400, detail="Solicitação inválida ou expirada.") from exc
    if payload.get("purpose") != _APPROVAL_PURPOSE:
        raise HTTPException(status_code=400, detail="Solicitação inválida ou expirada.")
    return payload


def _is_active(user: User) -> bool:
    if user.subscription_status != "active":
        return False
    expires = user.subscription_expires_at
    if expires is None:
        return True
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return expires > _now()


def _activate_user(user: User, days: int) -> None:
    now = _now()
    expires = user.subscription_expires_at
    if expires is not None and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    base = expires if expires and expires > now else now
    user.subscription_status = "active"
    user.subscription_activated_at = now
    user.subscription_expires_at = base + timedelta(days=days)


def _page(title: str, message: str, *, success: bool = True, form_html: str = "") -> HTMLResponse:
    accent = "#5b4df5" if success else "#b42318"
    body = f"""
    <!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{escape(title)} | Vynce</title></head>
    <body style="margin:0;background:#f5f7fb;font-family:Arial,sans-serif;color:#202534;">
      <main style="max-width:620px;margin:60px auto;padding:0 20px;">
        <section style="background:#fff;border:1px solid #e5e7eb;border-radius:18px;padding:34px;box-shadow:0 18px 50px rgba(31,41,55,.10)">
          <div style="font-size:13px;font-weight:800;letter-spacing:.08em;color:{accent};text-transform:uppercase">Vynce</div>
          <h1 style="font-size:26px;margin:8px 0 12px">{escape(title)}</h1>
          <p style="line-height:1.65;color:#667085">{escape(message)}</p>
          {form_html}
        </section>
      </main>
    </body></html>
    """
    return HTMLResponse(body)


@router.post("/request-activation")
def request_activation(current_user: User = Depends(get_current_user)):
    if _is_active(current_user):
        return {"status": "active", "message": "Sua conta já está ativa."}
    if current_user.subscription_status == "blocked":
        raise HTTPException(status_code=403, detail="Esta conta está bloqueada. Entre em contato com a Vynce.")

    token = _approval_token(current_user)
    review_link = f"{settings.BACKEND_PUBLIC_URL.rstrip('/')}/subscriptions/review?token={token}"
    html = base_email_html(
        "Solicitação de liberação de acesso",
        f'''
        <p>Uma conta solicitou liberação comercial da Vynce.</p>
        <p><strong>Cliente:</strong> {escape(current_user.name)}<br><strong>E-mail:</strong> {escape(current_user.email)}</p>
        <p>Confirme o pagamento fora da plataforma antes de autorizar.</p>
        <p style="margin:24px 0;"><a href="{review_link}" style="background:#5b4df5;color:#fff;padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:700;">Revisar e autorizar acesso</a></p>
        <p style="font-size:12px;color:#667085">Por segurança, o link expira em {settings.SUBSCRIPTION_APPROVAL_TOKEN_HOURS} horas e não libera a conta apenas por ser aberto.</p>
        ''',
    )
    try:
        send_email(
            settings.OWNER_CONTACT_EMAIL,
            f"Autorizar acesso Vynce — {current_user.email}",
            html,
            reply_to=current_user.email,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Não foi possível enviar a solicitação agora. Tente novamente em alguns minutos.") from exc

    return {
        "status": "pending",
        "message": f"Solicitação enviada para {settings.OWNER_CONTACT_EMAIL}. Após a confirmação do pagamento, o responsável poderá liberar seu acesso.",
    }


@router.get("/review", response_class=HTMLResponse)
def review_activation(token: str, db: Session = Depends(get_db)):
    payload = _decode_approval_token(token)
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Solicitação inválida ou expirada.") from exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.email != payload.get("email"):
        return _page("Solicitação inválida", "A conta desta solicitação não foi encontrada.", success=False)
    if user.subscription_status == "blocked":
        return _page("Conta bloqueada", "Esta conta está bloqueada e não pode ser liberada por este link.", success=False)
    if _is_active(user):
        return _page("Conta já liberada", f"O acesso de {user.email} já está ativo.")

    safe_token = escape(token, quote=True)
    form = f'''
    <div style="margin:20px 0;padding:14px;background:#f6f5ff;border-radius:10px;color:#4338ca">
      <strong>Conta:</strong> {escape(user.name)} &lt;{escape(user.email)}&gt;<br>
      <strong>Período:</strong> {settings.SUBSCRIPTION_DEFAULT_DAYS} dias
    </div>
    <form method="post" action="/subscriptions/approve">
      <input type="hidden" name="token" value="{safe_token}">
      <button type="submit" style="border:0;background:#111827;color:white;padding:12px 18px;border-radius:9px;font-weight:700;cursor:pointer">Autorizar acesso por {settings.SUBSCRIPTION_DEFAULT_DAYS} dias</button>
    </form>
    '''
    return _page("Confirmar liberação", "Confira o pagamento recebido antes de autorizar. Abrir este link, por si só, não ativa a conta.", form_html=form)


@router.post("/approve", response_class=HTMLResponse)
def approve_activation(token: str = Form(...), db: Session = Depends(get_db)):
    payload = _decode_approval_token(token)
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Solicitação inválida ou expirada.") from exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.email != payload.get("email"):
        return _page("Solicitação inválida", "A conta desta solicitação não foi encontrada.", success=False)
    if user.subscription_status == "blocked":
        return _page("Conta bloqueada", "Esta conta está bloqueada e não pode ser liberada por este link.", success=False)
    if _is_active(user):
        return _page("Conta já liberada", f"O acesso de {user.email} já estava ativo.")

    _activate_user(user, settings.SUBSCRIPTION_DEFAULT_DAYS)
    db.commit()

    try:
        html = base_email_html(
            "Seu acesso foi liberado",
            f'''<p>Olá, {escape(user.name)}!</p><p>Seu acesso à Vynce foi autorizado. Faça login novamente ou atualize a página para começar a usar a plataforma.</p>''',
        )
        send_email(user.email, "Acesso liberado — Vynce", html)
    except Exception:
        pass

    return _page("Acesso autorizado", f"A conta {user.email} foi liberada por {settings.SUBSCRIPTION_DEFAULT_DAYS} dias. O usuário já pode utilizar a Vynce.")


@router.post("/activate")
def activate(data: ActivationRequest, x_vynce_admin_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    _authorize(x_vynce_admin_key)
    user = db.query(User).filter(User.email == data.email.strip().lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Conta não encontrada.")
    _activate_user(user, data.days)
    db.commit()
    return {"status": "active", "email": user.email, "expires_at": user.subscription_expires_at}


@router.post("/block")
def block(data: ActivationRequest, x_vynce_admin_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    _authorize(x_vynce_admin_key)
    user = db.query(User).filter(User.email == data.email.strip().lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Conta não encontrada.")
    user.subscription_status = "blocked"
    db.commit()
    return {"status": "blocked", "email": user.email}
