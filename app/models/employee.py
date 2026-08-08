from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Employee(Base):
    """Colaborador pertencente a uma empresa/usuário do Vynce."""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)

    active = Column(Boolean, nullable=False, default=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    comandas = relationship(
        "Comanda",
        back_populates="employee",
        foreign_keys="Comanda.employee_id",
    )
