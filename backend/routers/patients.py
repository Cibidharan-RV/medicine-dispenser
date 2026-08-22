from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.patient import PatientOut, PatientUpdate
from backend.schemas.caregiver import CaregiverPatientOut
from backend.services import patient_service
from backend.auth.dependencies import get_current_user, require_role
from backend.models.user import User

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/", response_model=List[PatientOut])
def read_patients(db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR", "CAREGIVER", "ADMIN"))):
    return patient_service.get_patients(db)

@router.get("/{patient_id}", response_model=PatientOut)
def read_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # PATIENT can read themselves. DOCTOR/CAREGIVER/ADMIN can read anyone.
    if current_user.role == "PATIENT" and current_user.userid != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this patient")
    
    db_patient = patient_service.get_patient(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, patient_update: PatientUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "PATIENT" and current_user.userid != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this patient")
    return patient_service.update_patient(db, patient_id, patient_update)

@router.get("/{patient_id}/caregivers", response_model=List[CaregiverPatientOut])
def read_patient_caregivers(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "PATIENT" and current_user.userid != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return patient_service.get_caregivers_for_patient(db, patient_id)
