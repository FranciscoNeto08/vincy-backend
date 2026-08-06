from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Service(Base):
    """Serviço oferecido pelo estabelecimento (ex: corte, barba, escova)."""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False, default=0.0)
    duration = Column(Integer, nullable=True)  # duração em minutos
    description = Column(Text, nullable=True)

    active = Column(Boolean, default=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="services", foreign_keys=[owner_id])
