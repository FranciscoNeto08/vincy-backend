from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.marketing_permission import MarketingPermission

VALID_CHANNELS = {"email", "whatsapp"}


def set_permission(
    db: Session,
    *,
    owner_id: int,
    client_id: int,
    channel: str,
    allowed: bool,
    source: str = "manual",
    legal_basis_note: str | None = None,
    commit: bool = True,
) -> MarketingPermission:
    if channel not in VALID_CHANNELS:
        raise ValueError("Canal de marketing inválido.")

    now = datetime.now(timezone.utc)
    row = (
        db.query(MarketingPermission)
        .filter(
            MarketingPermission.owner_id == owner_id,
            MarketingPermission.client_id == client_id,
            MarketingPermission.channel == channel,
        )
        .first()
    )
    if row is None:
        row = MarketingPermission(
            owner_id=owner_id,
            client_id=client_id,
            channel=channel,
        )
        db.add(row)

    was_allowed = bool(row.allowed)
    row.allowed = bool(allowed)
    row.source = (source or "manual")[:50]
    row.legal_basis_note = (legal_basis_note or "")[:255] or None
    if allowed:
        # captured_at marca a manifestação positiva mais recente.
        row.captured_at = now
        row.revoked_at = None
    elif was_allowed:
        # Só chamamos de revogação quando havia permissão positiva anterior.
        row.revoked_at = now

    if commit:
        db.commit()
        db.refresh(row)
    return row


def is_allowed(db: Session, *, owner_id: int, client_id: int, channel: str) -> bool:
    row = (
        db.query(MarketingPermission)
        .filter(
            MarketingPermission.owner_id == owner_id,
            MarketingPermission.client_id == client_id,
            MarketingPermission.channel == channel,
            MarketingPermission.allowed.is_(True),
        )
        .first()
    )
    return row is not None
