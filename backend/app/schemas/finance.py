from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    type: Literal["entrada", "saida"]
    description: str = Field(min_length=1, max_length=255)
    amount: float = Field(gt=0, le=100_000_000, allow_inf_nan=False)
    comanda_id: int | None = Field(default=None, gt=0)


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
    periodo: str
    entradas: float
    saidas: float


class FinanceChart(BaseModel):
    pontos: list[FinanceChartPoint]
