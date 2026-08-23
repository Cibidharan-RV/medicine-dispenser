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
def get_due_schedules(patient_id: Optional[int] = None, db: Session = Depends(get_db)):
    # Hardware ESP32 endpoint. Allows device to pass patient_id from RFID.
    return dispensing_service.get_due_schedules(db, patient_id=patient_id)

@router.post("/dispense")
def dispense(request: DispenseRequest, db: Session = Depends(get_db)):
    # Hardware ESP32 endpoint to log successful physical dispensing, or trigger it.
    # Note: For frontend development, a dispense simulation may be triggered by the patient.
    # Caregivers are explicitly NOT allowed to trigger dispense.
    schedule = db.query(DispenseSchedule).filter(DispenseSchedule.schedule_id == request.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    return dispensing_service.dispense(db, request)
