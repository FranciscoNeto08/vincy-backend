from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityCreate(BaseModel):
    title: str
    priority: str = "Baixa"


class ActivityResponse(BaseModel):
    id: int
    title: str
    priority: str
    completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
