import os

os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_security.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-" + "x" * 40)

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.client import Client
from app.models.activity import Activity
from app.models.appointment import Appointment
from app.models.audit_log import AuditLog
from app.models.campaign import Campaign
from app.models.comanda import Comanda, ComandaItem
from app.models.email_token import EmailToken
from app.models.employee import Employee
from app.models.evolution import EvolutionConfig
from app.models.finance import Transaction
from app.models.history import History
from app.models.service import Service
from app.models.legal_acceptance import LegalAcceptance
from app.models.marketing_permission import MarketingPermission
from app.models.user import User
from app.schemas.client import ClientCreate
from app.schemas.user import UserCreate
from app.services.marketing_permission_service import is_allowed, set_permission


def test_registration_requires_legal_acknowledgement():
    with pytest.raises(ValidationError):
        UserCreate(name="Teste", email="teste@example.com", password="12345678")


def test_positive_marketing_permission_requires_source():
    with pytest.raises(ValidationError):
        ClientCreate(name="Cliente", email="c@example.com", email_marketing_opt_in=True)


def test_marketing_permission_is_channel_specific():
    engine = create_engine("sqlite:///:memory:")
    # Carrega apenas as tabelas necessárias para este teste.
    User.__table__.create(engine)
    Client.__table__.create(engine)
    MarketingPermission.__table__.create(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        user = User(name="Dono", email="dono@example.com", password="hash", email_verified=True)
        db.add(user); db.flush()
        client = Client(name="Cliente", owner_id=user.id)
        db.add(client); db.flush()
        set_permission(db, owner_id=user.id, client_id=client.id, channel="email", allowed=True, source="presencial")
        assert is_allowed(db, owner_id=user.id, client_id=client.id, channel="email") is True
        assert is_allowed(db, owner_id=user.id, client_id=client.id, channel="whatsapp") is False
    finally:
        db.close()
