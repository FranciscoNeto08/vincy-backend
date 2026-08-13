from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    note = Column(Text, nullable=True)
    unsubscribed = Column(Boolean, nullable=False, default=False, server_default="false")

    # Dono do cadastro (isolamento multi-tenant: cada usuário só vê seus clientes)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    owner = relationship("User", back_populates="clients", foreign_keys=[owner_id])
    comandas = relationship("Comanda", back_populates="client")
