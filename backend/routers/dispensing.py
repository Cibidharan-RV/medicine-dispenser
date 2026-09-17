from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend.schemas.schedule import DispenseScheduleOut
from backend.schemas.dispense import DispenseRequest, DispenseLogOut
from backend.services import dispensing_service, patient_service
from backend.auth.dependencies import get_current_user, require_role
from backend.models.user import User
from backend.models.dispense_schedule import DispenseSchedule
from backend.models.prescription_item import PrescriptionItem
from backend.models.prescription import Prescription
from backend.models.nfc_card import NfcCard
from backend.auth.hardware import verify_hardware_api_key

router = APIRouter(prefix="/dispensing", tags=["dispensing"])

@router.get("/history/{patient_id}", response_model=List[DispenseLogOut])
def get_dispense_history(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("PATIENT", "CAREGIVER", "DOCTOR"))):
    if current_user.role == "PATIENT" and current_user.userid != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role == "CAREGIVER":
        caregivers = patient_service.get_caregivers_for_patient(db, patient_id)
        if not any(c.caregiver_id == current_user.userid for c in caregivers):
            raise HTTPException(status_code=403, detail="Not authorized for this patient")
    return dispensing_service.get_dispense_history(db, patient_id)

@router.get("/due", response_model=List[DispenseScheduleOut])
def get_due_schedules(nfc_uid: str, db: Session = Depends(get_db), hw_key: str = Depends(verify_hardware_api_key)):
    card = db.query(NfcCard).filter(NfcCard.nfc_uid == nfc_uid, NfcCard.is_active == True).first()
    if not card:
        raise HTTPException(status_code=403, detail="Invalid or inactive NFC card")
    
    user = db.query(User).filter(User.userid == card.userid).first()
    if not user or user.role != "PATIENT":
        raise HTTPException(status_code=403, detail="Only PATIENT cards can trigger dispensing")

    return dispensing_service.get_due_schedules(db, patient_id=user.userid)

@router.post("/dispense")
def dispense(request: DispenseRequest, db: Session = Depends(get_db), hw_key: str = Depends(verify_hardware_api_key)):
    card = db.query(NfcCard).filter(NfcCard.nfc_uid == request.nfc_uid, NfcCard.is_active == True).first()
    if not card:
        raise HTTPException(status_code=403, detail="Invalid or inactive NFC card")
    
    user = db.query(User).filter(User.userid == card.userid).first()
    if not user or user.role != "PATIENT":
        raise HTTPException(status_code=403, detail="Only PATIENT cards can trigger dispensing")
        
    schedule = db.query(DispenseSchedule).filter(DispenseSchedule.schedule_id == request.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    presc = db.query(Prescription).join(PrescriptionItem).filter(PrescriptionItem.prescription_item_id == schedule.prescription_item_id).first()
    if presc.patient_id != user.userid:
        raise HTTPException(status_code=403, detail="Card does not match prescription")
        
    return dispensing_service.dispense(db, request)
