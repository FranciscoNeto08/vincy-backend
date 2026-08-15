from __future__ import annotations

import base64
import hashlib
import hmac
import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.settings import settings
from app.models.client import Client
from app.services.marketing_permission_service import set_permission

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def _verify_svix(request: Request, body: bytes) -> bool:
    secret = settings.RESEND_WEBHOOK_SECRET
    if not secret:
        return False

    msg_id = request.headers.get("svix-id")
    timestamp = request.headers.get("svix-timestamp")
    signature_header = request.headers.get("svix-signature")
    if not msg_id or not timestamp or not signature_header:
        return False

    try:
        ts = int(timestamp)
        if abs(time.time() - ts) > settings.RESEND_WEBHOOK_TOLERANCE_SECONDS:
            return False
        raw_secret = secret.split("_", 1)[1] if secret.startswith("whsec_") else secret
        key = base64.b64decode(raw_secret)
        signed = f"{msg_id}.{timestamp}.".encode() + body
        expected = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()
        return any(
            hmac.compare_digest(item.split(",", 1)[-1], expected)
            for item in signature_header.split()
            if "," in item
        )
    except (ValueError, TypeError):
        return False


@router.post("/resend")
async def resend_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    if not _verify_svix(request, body):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Assinatura inválida.")

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Payload inválido.") from exc

    event_type = payload.get("type", "")
    data = payload.get("data") or {}
    if event_type not in {"email.bounced", "email.complained"}:
        return {"received": True}

    email = str(data.get("to") or data.get("email") or "").strip().lower()
    if email:
        clients = db.query(Client).filter(Client.email.ilike(email)).all()
        for client in clients:
            client.unsubscribed = True
            set_permission(
                db,
                owner_id=client.owner_id,
                client_id=client.id,
                channel="email",
                allowed=False,
                source="provider_event",
                legal_basis_note=f"Resend {event_type}",
                commit=False,
            )
        db.commit()

    return {"received": True}
