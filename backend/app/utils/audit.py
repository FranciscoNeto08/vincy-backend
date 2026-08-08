from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def audit_event(
    db: Session,
    *,
    action: str,
    user_id: int | None = None,
    owner_id: int | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
    success: bool = True,
    detail: str | None = None,
) -> None:
    """Não inclua senhas, tokens, API keys ou conteúdo sensível em detail."""
    try:
        db.add(
            AuditLog(
                action=action[:80],
                user_id=user_id,
                owner_id=owner_id,
                ip=(ip or "")[:64] or None,
                user_agent=(user_agent or "")[:255] or None,
                request_id=(request_id or "")[:100] or None,
                success=success,
                detail=(detail or "")[:1000] or None,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        # Auditoria nunca deve derrubar a operação principal.
