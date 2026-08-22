from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.doctor import DoctorOut, DoctorUpdate
from backend.services import doctor_service
from backend.auth.dependencies import get_current_user, require_role
from backend.models.user import User

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.get("/", response_model=List[DoctorOut])
def read_doctors(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return doctor_service.get_doctors(db)

@router.get("/{doctor_id}", response_model=DoctorOut)
def read_doctor(doctor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_doctor = doctor_service.get_doctor(db, doctor_id)
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@router.put("/{doctor_id}", response_model=DoctorOut)
def update_doctor(doctor_id: int, doctor_update: DoctorUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR", "ADMIN"))):
    if current_user.role == "DOCTOR" and current_user.userid != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this doctor")
    return doctor_service.update_doctor(db, doctor_id, doctor_update)
