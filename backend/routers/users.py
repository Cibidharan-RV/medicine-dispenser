from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.user import UserCreate, UserOut, UserUpdate
from backend.services import user_service
from backend.auth.dependencies import get_current_user, require_role
from backend.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Assuming creating users requires some admin privilege or is open for registration
    # For now, let's keep it open or we can add a require_role("ADMIN") if we introduce an ADMIN role
    return user_service.create_user(db=db, user=user)

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.userid != user_id and current_user.role != "ADMIN": # Add ADMIN role check if introduced
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    return user_service.update_user(db=db, user_id=user_id, user_update=user)
