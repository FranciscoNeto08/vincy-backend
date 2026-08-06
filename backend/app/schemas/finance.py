from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    type: str  # "entrada" | "saida"
    description: str
    amount: float
    comanda_id: int | None = None


class TransactionResponse(BaseModel):
    id: int
    type: str
    description: str
    amount: float
    comanda_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FinanceSummary(BaseModel):
    total_entradas: float
    total_saidas: float
    lucro: float

class FinanceChartPoint(BaseModel):
    periodo: str  # ex: "2026-08"
    entradas: float
    saidas: float


class FinanceChart(BaseModel):
    pontos: list[FinanceChartPoint]
