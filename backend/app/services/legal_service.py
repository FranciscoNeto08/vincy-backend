from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.legal_acceptance import LegalAcceptance


def current_legal_status(db: Session, user_id: int) -> dict:
    rows = (
        db.query(LegalAcceptance.document_type, LegalAcceptance.document_version, LegalAcceptance.accepted_at)
        .filter(LegalAcceptance.user_id == user_id)
        .all()
    )
    accepted = {(row[0], row[1]) for row in rows}
    terms_ok = ("terms", settings.TERMS_VERSION) in accepted
    privacy_ok = ("privacy", settings.PRIVACY_VERSION) in accepted
    return {
        "terms_version": settings.TERMS_VERSION,
        "privacy_version": settings.PRIVACY_VERSION,
        "terms_accepted": terms_ok,
        "privacy_acknowledged": privacy_ok,
        "complete": terms_ok and privacy_ok,
    }


def accept_current_documents(
    db: Session,
    *,
    user_id: int,
    terms_accepted: bool,
    privacy_acknowledged: bool,
    ip_address: str | None,
    user_agent: str | None,
    request_id: str | None,
) -> dict:
    if not terms_accepted or not privacy_acknowledged:
        raise ValueError("Os documentos legais vigentes precisam ser aceitos/confirmados.")

    common = {
        "user_id": user_id,
        "ip_address": (ip_address or "")[:64] or None,
        "user_agent": (user_agent or "")[:255] or None,
        "request_id": (request_id or "")[:100] or None,
    }
    status = current_legal_status(db, user_id)
    if not status["terms_accepted"]:
        db.add(LegalAcceptance(document_type="terms", document_version=settings.TERMS_VERSION, **common))
    if not status["privacy_acknowledged"]:
        db.add(LegalAcceptance(document_type="privacy", document_version=settings.PRIVACY_VERSION, **common))
    db.commit()
    return current_legal_status(db, user_id)
