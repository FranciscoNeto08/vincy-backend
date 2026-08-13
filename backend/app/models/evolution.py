# app/models/evolution.py

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.config.database import Base


class EvolutionConfig(Base):
    """Configuração da Evolution API para integração com WhatsApp."""

    __tablename__ = "evolution_configs"

    id = Column(Integer, primary_key=True, index=True)

    # Credenciais
    api_key = Column(String(255), nullable=False)
    base_url = Column(String(255), nullable=False)
    instance_name = Column(String(100), default="default", nullable=False)

    # Status
    active = Column(Boolean, default=True, nullable=False)

    # Proprietário
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<EvolutionConfig {self.id} - {self.instance_name}>"
