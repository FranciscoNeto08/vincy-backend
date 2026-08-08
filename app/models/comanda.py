from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Comanda(Base):
    """Comanda de atendimento: agrupa um cliente, colaborador e serviços realizados."""

    __tablename__ = "comandas"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )

    # Usuário dono da sessão que abriu a comanda.
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    # Profissional que realizou o atendimento.
    # Nullable preserva comandas antigas que ainda não tinham colaborador.
    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=True,
        index=True,
    )

    # status: aberta | finalizada | cancelada
    status = Column(
        String(20),
        nullable=False,
        default="aberta",
    )

    total = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    data_abertura = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    data_fechamento = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    client = relationship(
        "Client",
        back_populates="comandas",
    )

    items = relationship(
        "ComandaItem",
        back_populates="comanda",
        cascade="all, delete-orphan",
    )

    owner = relationship(
        "User",
        back_populates="comandas",
        foreign_keys=[owner_id],
    )

    attendant = relationship(
        "User",
        foreign_keys=[user_id],
    )

    employee = relationship(
        "Employee",
        back_populates="comandas",
        foreign_keys=[employee_id],
    )

    @property
    def client_name(self) -> str | None:
        return self.client.name if self.client else None

    @property
    def employee_name(self) -> str | None:
        return self.employee.name if self.employee else None


class ComandaItem(Base):
    """Serviço adicionado a uma comanda (item da comanda)."""

    __tablename__ = "comanda_items"

    id = Column(Integer, primary_key=True, index=True)

    comanda_id = Column(
        Integer,
        ForeignKey("comandas.id"),
        nullable=False,
        index=True,
    )

    service_id = Column(
        Integer,
        ForeignKey("services.id"),
        nullable=True,
    )

    # Nome/preço no momento em que o item foi adicionado à comanda.
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    comanda = relationship(
        "Comanda",
        back_populates="items",
    )
