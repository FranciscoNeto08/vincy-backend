from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class MarketingPermission(Base):
    """Permissão/oposição estruturada por cliente e canal."""

    __tablename__ = "client_marketing_permissions"
    __table_args__ = (
        UniqueConstraint("client_id", "channel", name="uq_client_marketing_permission_channel"),
    )

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    channel = Column(String(20), nullable=False, index=True)  # email | whatsapp
    allowed = Column(Boolean, nullable=False, default=False, server_default="false")
    source = Column(String(50), nullable=False, default="not_informed")
    legal_basis_note = Column(String(255), nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    client = relationship("Client", back_populates="marketing_permissions", foreign_keys=[client_id])
