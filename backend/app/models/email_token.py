from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class EmailToken(Base):
    """Token de uso único para confirmar e-mail ou redefinir senha."""

    __tablename__ = "email_tokens"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    # Guarda SHA-256 do token; o valor em texto puro existe apenas no link enviado.
    token = Column(String(64), unique=True, nullable=False, index=True)

    kind = Column(String(20), nullable=False)  # "verify_email" | "reset_password"

    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
