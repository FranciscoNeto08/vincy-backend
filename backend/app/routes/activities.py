from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_subscriber
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse

router = APIRouter(prefix="/activities", tags=["Atividades"])


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    activity = Activity(title=data.title, priority=data.priority, owner_id=current_user.id)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.get("", response_model=list[ActivityResponse])
def list_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    return (
        db.query(Activity)
        .filter(Activity.owner_id == current_user.id)
        .order_by(Activity.created_at.desc())
        .all()
    )


@router.patch("/{activity_id}/toggle", response_model=ActivityResponse)
def toggle_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id, Activity.owner_id == current_user.id)
        .first()
    )
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atividade não encontrada.")

    activity.completed = not activity.completed
    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_subscriber),
):
    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id, Activity.owner_id == current_user.id)
        .first()
    )
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atividade não encontrada.")

    db.delete(activity)
    db.commit()
