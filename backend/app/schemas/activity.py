from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ActivityCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    priority: Literal["Baixa", "Media", "Alta"] = "Baixa"


class ActivityResponse(BaseModel):
    id: int
    title: str
    priority: str
    completed: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
