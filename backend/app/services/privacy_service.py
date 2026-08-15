from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.security import verify_and_upgrade_password
from app.config.settings import settings
from app.models.activity import Activity
from app.models.appointment import Appointment
from app.models.audit_log import AuditLog
from app.models.campaign import Campaign
from app.models.client import Client
from app.models.comanda import Comanda, ComandaItem
from app.models.email_token import EmailToken
from app.models.employee import Employee
from app.models.evolution import EvolutionConfig
from app.models.finance import Transaction
from app.models.history import History
from app.models.legal_acceptance import LegalAcceptance
from app.models.marketing_permission import MarketingPermission
from app.models.service import Service
from app.models.user import User


DELETE_CONFIRMATION = "EXCLUIR MINHA CONTA"


def permanently_delete_account(
    db: Session,
    *,
    user: User,
    current_password: str,
    confirmation: str,
) -> None:
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contas administrativas não podem ser removidas por autoatendimento.",
        )
    if confirmation.strip().upper() != DELETE_CONFIRMATION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Digite exatamente "{DELETE_CONFIRMATION}" para confirmar.',
        )
    valid, _ = verify_and_upgrade_password(current_password, user.password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta.")

    owner_id = user.id
    try:
        # Preserva somente logs estritamente necessários, sem vínculo identificador com a conta removida.
        db.query(AuditLog).filter(
            (AuditLog.user_id == owner_id) | (AuditLog.owner_id == owner_id)
        ).update(
            {
                AuditLog.user_id: None,
                AuditLog.owner_id: None,
                AuditLog.detail: "conta removida; identificadores desvinculados",
            },
            synchronize_session=False,
        )

        comanda_ids = [row[0] for row in db.query(Comanda.id).filter(Comanda.owner_id == owner_id).all()]
        if comanda_ids:
            db.query(History).filter(History.comanda_id.in_(comanda_ids)).delete(synchronize_session=False)
            db.query(Transaction).filter(Transaction.comanda_id.in_(comanda_ids)).delete(synchronize_session=False)
            db.query(ComandaItem).filter(ComandaItem.comanda_id.in_(comanda_ids)).delete(synchronize_session=False)

        client_ids = [row[0] for row in db.query(Client.id).filter(Client.owner_id == owner_id).all()]
        if client_ids:
            db.query(MarketingPermission).filter(MarketingPermission.client_id.in_(client_ids)).delete(synchronize_session=False)

        db.query(Appointment).filter(Appointment.owner_id == owner_id).delete(synchronize_session=False)
        db.query(History).filter(History.owner_id == owner_id).delete(synchronize_session=False)
        db.query(Transaction).filter(Transaction.owner_id == owner_id).delete(synchronize_session=False)
        db.query(ComandaItem).filter(ComandaItem.comanda_id.in_(comanda_ids or [-1])).delete(synchronize_session=False)
        db.query(Comanda).filter(Comanda.owner_id == owner_id).delete(synchronize_session=False)
        db.query(Campaign).filter(Campaign.owner_id == owner_id).delete(synchronize_session=False)
        db.query(Activity).filter(Activity.owner_id == owner_id).delete(synchronize_session=False)
        db.query(EvolutionConfig).filter(EvolutionConfig.owner_id == owner_id).delete(synchronize_session=False)
        db.query(Employee).filter(Employee.owner_id == owner_id).delete(synchronize_session=False)
        db.query(MarketingPermission).filter(MarketingPermission.owner_id == owner_id).delete(synchronize_session=False)
        db.query(Client).filter(Client.owner_id == owner_id).delete(synchronize_session=False)
        db.query(Service).filter(Service.owner_id == owner_id).delete(synchronize_session=False)
        db.query(EmailToken).filter(EmailToken.user_id == owner_id).delete(synchronize_session=False)
        db.query(LegalAcceptance).filter(LegalAcceptance.user_id == owner_id).delete(synchronize_session=False)
        db.delete(user)
        db.commit()
    except Exception:
        db.rollback()
        raise


def cleanup_expired_security_data(db: Session) -> dict:
    """Rotina executável por admin/cron para reduzir retenção desnecessária."""
    now = datetime.now(timezone.utc)
    token_cutoff = now - timedelta(days=settings.EXPIRED_TOKEN_RETENTION_DAYS)
    audit_cutoff = now - timedelta(days=settings.AUDIT_LOG_RETENTION_DAYS)

    expired_tokens = db.query(EmailToken).filter(
        EmailToken.expires_at < token_cutoff
    ).delete(synchronize_session=False)

    old_audits = db.query(AuditLog).filter(
        AuditLog.created_at < audit_cutoff
    ).delete(synchronize_session=False)

    db.commit()
    return {"expired_tokens_deleted": expired_tokens, "audit_logs_deleted": old_audits}


def export_account_data(db: Session, *, user: User) -> dict:
    """Exporta dados da conta sem hashes de senha, tokens ou segredos de integração."""
    owner_id = user.id

    def iso(value):
        return value.isoformat() if value is not None and hasattr(value, "isoformat") else value

    clients = db.query(Client).filter(Client.owner_id == owner_id).order_by(Client.id).all()
    services = db.query(Service).filter(Service.owner_id == owner_id).order_by(Service.id).all()
    employees = db.query(Employee).filter(Employee.owner_id == owner_id).order_by(Employee.id).all()
    activities = db.query(Activity).filter(Activity.owner_id == owner_id).order_by(Activity.id).all()
    transactions = db.query(Transaction).filter(Transaction.owner_id == owner_id).order_by(Transaction.id).all()
    appointments = db.query(Appointment).filter(Appointment.owner_id == owner_id).order_by(Appointment.id).all()
    campaigns = db.query(Campaign).filter(Campaign.owner_id == owner_id).order_by(Campaign.id).all()
    comandas = db.query(Comanda).filter(Comanda.owner_id == owner_id).order_by(Comanda.id).all()
    history = db.query(History).filter(History.owner_id == owner_id).order_by(History.id).all()
    legal = db.query(LegalAcceptance).filter(LegalAcceptance.user_id == owner_id).order_by(LegalAcceptance.id).all()
    permissions = db.query(MarketingPermission).filter(MarketingPermission.owner_id == owner_id).order_by(MarketingPermission.id).all()

    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "account": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "theme": user.theme,
            "role": user.role,
            "active": bool(user.active),
            "email_verified": bool(user.email_verified),
            "created_at": iso(user.created_at),
            "password_changed_at": iso(user.password_changed_at),
        },
        "clients": [
            {
                "id": c.id, "name": c.name, "phone": c.phone, "email": c.email,
                "note": c.note, "unsubscribed": bool(c.unsubscribed),
                "created_at": iso(c.created_at), "updated_at": iso(c.updated_at),
            } for c in clients
        ],
        "marketing_permissions": [
            {
                "client_id": p.client_id, "channel": p.channel, "allowed": bool(p.allowed),
                "source": p.source, "legal_basis_note": p.legal_basis_note,
                "captured_at": iso(p.captured_at), "revoked_at": iso(p.revoked_at),
            } for p in permissions
        ],
        "services": [
            {"id": x.id, "name": x.name, "price": x.price, "duration": getattr(x, "duration", None), "description": x.description, "active": bool(x.active), "created_at": iso(x.created_at)}
            for x in services
        ],
        "employees": [
            {"id": x.id, "name": x.name, "phone": x.phone, "email": x.email, "active": bool(x.active), "created_at": iso(x.created_at)}
            for x in employees
        ],
        "activities": [
            {"id": x.id, "title": x.title, "priority": x.priority, "completed": bool(x.completed), "created_at": iso(x.created_at)}
            for x in activities
        ],
        "transactions": [
            {"id": x.id, "type": x.type, "description": x.description, "amount": x.amount, "comanda_id": x.comanda_id, "created_at": iso(x.created_at)}
            for x in transactions
        ],
        "appointments": [
            {"id": x.id, "client_id": x.client_id, "service_id": x.service_id, "scheduled_at": iso(x.scheduled_at), "reminder_minutes_before": x.reminder_minutes_before, "notes": x.notes, "status": x.status, "created_at": iso(x.created_at)}
            for x in appointments
        ],
        "campaigns": [
            {"id": x.id, "channel": x.channel, "subject": x.subject, "message": x.message, "total_destinatarios": x.total_destinatarios, "total_enviados": x.total_enviados, "total_falhas": x.total_falhas, "created_at": iso(x.created_at)}
            for x in campaigns
        ],
        "comandas": [
            {"id": x.id, "client_id": x.client_id, "employee_id": x.employee_id, "status": x.status, "total": x.total, "data_abertura": iso(x.data_abertura), "data_fechamento": iso(x.data_fechamento),
             "items": [{"id": i.id, "service_id": i.service_id, "name": i.name, "price": i.price, "quantity": i.quantity} for i in x.items]}
            for x in comandas
        ],
        "history": [
            {"id": x.id, "comanda_id": x.comanda_id, "action": x.action, "usuario": x.usuario, "data": iso(x.data)}
            for x in history
        ],
        "legal_acceptances": [
            {"document_type": x.document_type, "document_version": x.document_version, "accepted_at": iso(x.accepted_at)}
            for x in legal
        ],
    }
