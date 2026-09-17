from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.user import UserCreate, UserOut, UserUpdate, NfcCardCreate
from backend.services import user_service
from backend.auth.dependencies import get_current_user, require_role
from backend.models.user import User
from backend.models.nfc_card import NfcCard

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Open for registration or restricted as per project needs
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
    if current_user.userid != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    return user_service.update_user(db=db, user_id=user_id, user_update=user)

@router.post("/{user_id}/nfc-cards", status_code=status.HTTP_201_CREATED)
def assign_nfc_card(user_id: int, card: NfcCardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Any authenticated user can assign a card to themselves (or DOCTOR can assign to anyone)
    if current_user.role != "DOCTOR" and current_user.userid != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to assign card to this user")
        
    db_user = user_service.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if card already exists
    existing = db.query(NfcCard).filter(NfcCard.nfc_uid == card.nfc_uid).first()
    if existing:
        raise HTTPException(status_code=400, detail="NFC UID already registered")
        
    new_card = NfcCard(userid=user_id, nfc_uid=card.nfc_uid)
    db.add(new_card)
    db.commit()
    return {"status": "success", "detail": "NFC card assigned"}
