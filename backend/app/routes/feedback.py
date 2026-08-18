from datetime import datetime, timezone
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.comanda import Comanda

router=APIRouter(prefix="/feedback", tags=["Feedback"])
class FeedbackIn(BaseModel):
    token: str = Field(min_length=20,max_length=200)
    rating: int = Field(ge=1,le=5)
    comment: str | None = Field(default=None,max_length=1000)

def _find(db,token):
    h=hashlib.sha256(token.encode("utf-8")).hexdigest()
    c=db.query(Comanda).filter(Comanda.feedback_token_hash==h).first()
    if not c: raise HTTPException(status_code=404,detail="Link de avaliação inválido.")
    exp=c.feedback_expires_at
    if exp and exp.tzinfo is None: exp=exp.replace(tzinfo=timezone.utc)
    if exp and exp < datetime.now(timezone.utc): raise HTTPException(status_code=410,detail="Este link de avaliação expirou.")
    return c
@router.get("/public")
def info(token:str, db:Session=Depends(get_db)):
    c=_find(db,token)
    return {"client_name":c.client_name,"already_answered":c.feedback_responded_at is not None}
@router.post("/public",status_code=201)
def submit(data:FeedbackIn, db:Session=Depends(get_db)):
    c=_find(db,data.token)
    if c.feedback_responded_at: raise HTTPException(status_code=409,detail="Esta avaliação já foi enviada.")
    c.feedback_rating=data.rating; c.feedback_comment=(data.comment or '').strip() or None; c.feedback_responded_at=datetime.now(timezone.utc)
    # uso único: invalida o token após resposta
    c.feedback_token_hash=None
    db.commit(); return {"message":"Obrigado pelo feedback!"}
