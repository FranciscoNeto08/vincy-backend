from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import authenticate_user, generate_token_for_user, register_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Cadastra um novo usuário no sistema."""
    return register_user(db, user_data)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login via OAuth2 (username = e-mail).
    Retorna um token JWT para ser usado em 'Authorization: Bearer <token>'.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    token = generate_token_for_user(user)
    return Token(access_token=token)
