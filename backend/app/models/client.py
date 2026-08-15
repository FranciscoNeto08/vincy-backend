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
    marketing_permissions = relationship(
        "MarketingPermission",
        back_populates="client",
        cascade="all, delete-orphan",
        foreign_keys="MarketingPermission.client_id",
    )

    @property
    def email_marketing_allowed(self) -> bool:
        return any(p.channel == "email" and bool(p.allowed) for p in self.marketing_permissions)

    @property
    def whatsapp_marketing_allowed(self) -> bool:
        return any(p.channel == "whatsapp" and bool(p.allowed) for p in self.marketing_permissions)

    @property
    def marketing_permission_source(self) -> str:
        for p in self.marketing_permissions:
            if p.allowed and p.source:
                return p.source
        for p in self.marketing_permissions:
            if p.source:
                return p.source
        return "not_informed"

    @property
    def marketing_legal_basis_note(self) -> str | None:
        for p in self.marketing_permissions:
            if p.legal_basis_note:
                return p.legal_basis_note
        return None
