from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Appointment(Base):
    """Agendamento de um cliente/serviço em um dia e horário, com lembrete."""

    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)

    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    reminder_minutes_before = Column(Integer, default=60)
    notes = Column(Text, nullable=True)

    status = Column(String(20), default="agendado")  # agendado | concluido | cancelado
    notified = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", foreign_keys=[owner_id])
    client = relationship("Client", foreign_keys=[client_id])
    service = relationship("Service", foreign_keys=[service_id])
