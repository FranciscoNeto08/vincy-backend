from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(150), unique=True, nullable=False, index=True)

    password = Column(String(255), nullable=False)

    phone = Column(String(20), nullable=True)

    theme = Column(String(10), default="escuro")  # "escuro" | "claro"

    role = Column(String(30), default="funcionario")

    active = Column(Boolean, default=True)

    # Confirmação de e-mail: enquanto False, o login é bloqueado.
    email_verified = Column(Boolean, default=False, nullable=False)

    # Proteção contra força bruta no login.
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Dados que pertencem a este usuário (isolamento multi-tenant via owner_id)
    clients = relationship("Client", back_populates="owner", foreign_keys="Client.owner_id")
    services = relationship("Service", back_populates="owner", foreign_keys="Service.owner_id")
    comandas = relationship("Comanda", back_populates="owner", foreign_keys="Comanda.owner_id")
    transactions = relationship("Transaction", back_populates="owner", foreign_keys="Transaction.owner_id")
    activities = relationship("Activity", back_populates="owner", foreign_keys="Activity.owner_id")
    history_entries = relationship("History", back_populates="owner", foreign_keys="History.owner_id")