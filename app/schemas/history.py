from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoryResponse(BaseModel):
    id: int
    comanda_id: int
    action: str
    usuario: str
    data: datetime

    model_config = ConfigDict(from_attributes=True)
