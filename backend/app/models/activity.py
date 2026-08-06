from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Activity(Base):
    """
    Atividade/tarefa do usuário (ex: 'ligar para fornecedor', 'organizar estoque').
    Usada na aba 'Atividades' do dashboard.
    """

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(150), nullable=False)
    priority = Column(String(20), nullable=False, default="Baixa")  # Baixa | Media | Alta
    completed = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="activities", foreign_keys=[owner_id])
