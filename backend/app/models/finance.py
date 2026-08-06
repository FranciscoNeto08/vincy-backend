from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Transaction(Base):
    """Lançamento financeiro (entrada ou saída) do estabelecimento."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    type = Column(String(10), nullable=False)  # "entrada" | "saida"
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)

    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="transactions", foreign_keys=[owner_id])
