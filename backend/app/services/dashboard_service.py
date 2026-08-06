from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.comanda import Comanda, ComandaItem
from app.models.service import Service


def get_dashboard_data(db: Session, owner_id: int) -> dict:
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_clients = db.query(Client).filter(Client.owner_id == owner_id).count()

    open_comandas = (
        db.query(Comanda)
        .filter(Comanda.owner_id == owner_id, Comanda.status == "aberta")
        .count()
    )

    revenue_today = (
        db.query(func.coalesce(func.sum(Comanda.total), 0.0))
        .filter(
            Comanda.owner_id == owner_id,
            Comanda.status == "finalizada",
            Comanda.data_fechamento >= today_start,
        )
        .scalar()
    )

    revenue_month = (
        db.query(func.coalesce(func.sum(Comanda.total), 0.0))
        .filter(
            Comanda.owner_id == owner_id,
            Comanda.status == "finalizada",
            Comanda.data_fechamento >= month_start,
        )
        .scalar()
    )

    revenue_total = (
        db.query(func.coalesce(func.sum(Comanda.total), 0.0))
        .filter(Comanda.owner_id == owner_id, Comanda.status == "finalizada")
        .scalar()
    )

    top_services = (
        db.query(
            Service.name,
            func.coalesce(func.sum(ComandaItem.quantity), 0).label("total_vendido"),
        )
        .join(ComandaItem, ComandaItem.service_id == Service.id)
        .join(Comanda, Comanda.id == ComandaItem.comanda_id)
        .filter(Comanda.owner_id == owner_id, Comanda.status == "finalizada")
        .group_by(Service.name)
        .order_by(func.sum(ComandaItem.quantity).desc())
        .limit(5)
        .all()
    )

    top_clients = (
        db.query(
            Client.name,
            func.count(Comanda.id).label("total_comandas"),
        )
        .join(Comanda, Comanda.client_id == Client.id)
        .filter(Comanda.owner_id == owner_id, Comanda.status == "finalizada")
        .group_by(Client.name)
        .order_by(func.count(Comanda.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_clientes": total_clients,
        "comandas_abertas": open_comandas,
        "receita_dia": revenue_today,
        "receita_mes": revenue_month,
        "receita_total": revenue_total,
        "servicos_mais_vendidos": [
            {"nome": nome, "quantidade": qtd} for nome, qtd in top_services
        ],
        "clientes_mais_frequentes": [
            {"nome": nome, "comandas": total} for nome, total in top_clients
        ],
    }
