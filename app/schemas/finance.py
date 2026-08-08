from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    type: Literal["entrada", "saida"]
    description: str = Field(min_length=1)
    amount: float = Field(gt=0, description="Valor precisa ser maior que zero")
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
