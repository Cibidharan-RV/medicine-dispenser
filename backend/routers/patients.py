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
def read_patients(db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR", "CAREGIVER"))):
    return patient_service.get_patients(db, current_user)

@router.get("/{patient_id}", response_model=PatientOut)
def read_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # PATIENT can read themselves. DOCTOR can read anyone. CAREGIVER can read assigned.
    if current_user.role == "PATIENT" and current_user.userid != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this patient")
    if current_user.role == "CAREGIVER":
        caregivers = patient_service.get_caregivers_for_patient(db, patient_id)
        if not any(c.caregiver_id == current_user.userid for c in caregivers):
            raise HTTPException(status_code=403, detail="Not authorized for this patient")
    
    db_patient = patient_service.get_patient(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, patient_update: PatientUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "PATIENT" and current_user.userid != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this patient")
    if current_user.role == "CAREGIVER":
        caregivers = patient_service.get_caregivers_for_patient(db, patient_id)
        if not any(c.caregiver_id == current_user.userid for c in caregivers):
            raise HTTPException(status_code=403, detail="Not authorized for this patient")
    return patient_service.update_patient(db, patient_id, patient_update)

from backend.schemas.prescription import PrescriptionOut
from backend.schemas.schedule import DispenseScheduleOut
from backend.models.prescription import Prescription
from backend.models.prescription_item import PrescriptionItem
from backend.models.dispense_schedule import DispenseSchedule

@router.get("/{patient_id}/caregivers", response_model=List[CaregiverPatientOut])
def read_patient_caregivers(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "PATIENT" and current_user.userid != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role == "CAREGIVER":
        caregivers = patient_service.get_caregivers_for_patient(db, patient_id)
        if not any(c.caregiver_id == current_user.userid for c in caregivers):
            raise HTTPException(status_code=403, detail="Not authorized for this patient")
    return patient_service.get_caregivers_for_patient(db, patient_id)

@router.get("/{patient_id}/prescriptions", response_model=List[PrescriptionOut])
def read_patient_prescriptions(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "PATIENT" and current_user.userid != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role == "CAREGIVER":
        caregivers = patient_service.get_caregivers_for_patient(db, patient_id)
        if not any(c.caregiver_id == current_user.userid for c in caregivers):
            raise HTTPException(status_code=403, detail="Not authorized for this patient")
    
    return db.query(Prescription).filter(Prescription.patient_id == patient_id).all()

@router.get("/{patient_id}/schedules", response_model=List[DispenseScheduleOut])
def read_patient_schedules(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "PATIENT" and current_user.userid != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role == "CAREGIVER":
        caregivers = patient_service.get_caregivers_for_patient(db, patient_id)
        if not any(c.caregiver_id == current_user.userid for c in caregivers):
            raise HTTPException(status_code=403, detail="Not authorized for this patient")
            
    # Join Schedule -> Item -> Prescription -> Patient
    schedules = db.query(DispenseSchedule).join(
        PrescriptionItem, DispenseSchedule.prescription_item_id == PrescriptionItem.prescription_item_id
    ).join(
        Prescription, PrescriptionItem.prescription_id == Prescription.prescription_id
    ).filter(Prescription.patient_id == patient_id).all()
    
    return schedules
