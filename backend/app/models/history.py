from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class History(Base):
    """Histórico de ações realizadas em uma comanda específica."""

    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)

    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # ex: "comanda aberta", "serviço adicionado"
    usuario = Column(String(100), nullable=False)  # nome de quem realizou a ação

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    data = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="history_entries", foreign_keys=[owner_id])
    comanda = relationship("Comanda")
