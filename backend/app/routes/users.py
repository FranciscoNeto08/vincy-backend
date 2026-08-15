from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import (
    get_authenticated_user,
    get_current_admin,
    get_current_user,
    hash_password,
    verify_and_upgrade_password,
)
from app.config.settings import settings
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth_service import send_new_verification_after_email_change
from app.utils.audit import audit_event

router = APIRouter(prefix="/users", tags=["Usuários"])


def _audit_meta(request: Request):
    return {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "request_id": request.scope.get("vynce.request_id"),
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_authenticated_user)):
    return current_user


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(User).order_by(User.name).limit(1000).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    update_data = data.model_dump(exclude_unset=True)

    if current_user.role != "admin":
        update_data.pop("role", None)
        update_data.pop("active", None)

    current_password = update_data.pop("current_password", None)
    password_changed = False
    reauth_validated = False

    if update_data.get("password"):
        if current_user.id == user_id:
            if not current_password:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta.")
            valid, upgraded = verify_and_upgrade_password(current_password, user.password)
            if not valid:
                audit_event(
                    db,
                    action="user.password_change",
                    user_id=current_user.id,
                    owner_id=current_user.id,
                    success=False,
                    detail="senha atual recusada",
                    **_audit_meta(request),
                )
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta.")
            if upgraded:
                user.password = upgraded
            reauth_validated = True

        user.password = hash_password(update_data.pop("password"))
        user.password_changed_at = datetime.now(timezone.utc)
        user.token_version = int(user.token_version or 0) + 1
        password_changed = True
    else:
        update_data.pop("password", None)

    email_changed = False
    if "email" in update_data and update_data["email"] is not None:
        new_email = str(update_data["email"]).strip().lower()
        if new_email != user.email.lower():
            # Alterar o identificador de login é uma operação sensível: exige reautenticação
            # quando o próprio usuário faz a mudança.
            if current_user.id == user_id and not reauth_validated:
                if not current_password:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informe a senha atual para alterar o e-mail.")
                valid_email_change, upgraded_email_hash = verify_and_upgrade_password(current_password, user.password)
                if not valid_email_change:
                    audit_event(db, action="user.email_change", user_id=current_user.id, owner_id=current_user.id, success=False, detail="senha atual recusada", **_audit_meta(request))
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta.")
                if upgraded_email_hash:
                    user.password = upgraded_email_hash
                reauth_validated = True

            existing = db.query(User).filter(User.email == new_email, User.id != user.id).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não foi possível usar esse e-mail.")
            update_data["email"] = new_email
            if settings.REQUIRE_EMAIL_VERIFICATION:
                user.email_verified = False
            # Invalida sessões antigas quando o identificador de login muda.
            user.token_version = int(user.token_version or 0) + 1
            email_changed = True

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    if email_changed:
        send_new_verification_after_email_change(db, user)

    audit_event(
        db,
        action="user.update",
        user_id=current_user.id,
        owner_id=user.id,
        detail=f"password_changed={password_changed}; email_changed={email_changed}",
        **_audit_meta(request),
    )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível excluir a própria conta administrativa por esta rota.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    # Soft delete reduz risco de quebrar histórico/FKs.
    user.active = False
    user.token_version = int(user.token_version or 0) + 1
    db.commit()

    audit_event(
        db,
        action="user.deactivate",
        user_id=current_user.id,
        owner_id=user.id,
        **_audit_meta(request),
    )
