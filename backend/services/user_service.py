from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.models.user import User
from backend.models.patient import Patient
from backend.models.doctor import Doctor
from backend.models.caregiver import Caregiver
from backend.schemas.user import UserCreate, UserUpdate
from backend.auth.security import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.userid == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        phone_number=user.phone_number
    )
    db.add(new_user)
    db.flush() # To get the userid for role-specific tables

    # Add to specific role table (basic instantiation)
    if user.role == "PATIENT":
        # Additional patient info will be added via patient endpoints
        # Using dummy data to satisfy constraints for now, real data should be added properly
        from datetime import date
        from backend.models.nfc_card import NfcCard
        db.add(Patient(userid=new_user.userid, date_of_birth=date(1900, 1, 1)))
        db.flush()
        if user.nfc_uid:
            db.add(NfcCard(nfc_uid=user.nfc_uid, userid=new_user.userid, is_active=True))
    elif user.role == "DOCTOR":
        db.add(Doctor(userid=new_user.userid, medical_registration_number=f"TBD-{new_user.userid}", specialization="TBD"))
    elif user.role == "CAREGIVER":
        db.add(Caregiver(userid=new_user.userid))

    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.commit()
    db.refresh(db_user)
    return db_user
