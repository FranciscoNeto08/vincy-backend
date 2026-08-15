from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class LegalAcceptance(Base):
    """Evidência versionada de aceite/ciência de documentos legais."""

    __tablename__ = "legal_acceptances"
    __table_args__ = (UniqueConstraint("user_id", "document_type", "document_version", name="uq_legal_acceptance_user_doc_version"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_type = Column(String(30), nullable=False, index=True)  # terms | privacy
    document_version = Column(String(30), nullable=False)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(255), nullable=True)
    request_id = Column(String(100), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
