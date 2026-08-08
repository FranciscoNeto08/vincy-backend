from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Campaign(Base):
    """Registro de um disparo de marketing (e-mail ou WhatsApp)."""

    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)

    channel = Column(String(10), nullable=False)  # "email" | "whatsapp"
    subject = Column(String(200), nullable=True)  # usado só no e-mail
    message = Column(Text, nullable=False)

    total_destinatarios = Column(Integer, default=0)
    total_enviados = Column(Integer, default=0)
    total_falhas = Column(Integer, default=0)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", foreign_keys=[owner_id])
