from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.schemas.prescription import PrescriptionCreate, PrescriptionOut, PrescriptionUpdate, PrescriptionItemOut
from backend.services import prescription_service
from backend.auth.dependencies import get_current_user, require_role
from backend.models.user import User

from backend.services import patient_service

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

@router.get("/", response_model=List[PrescriptionOut])
def read_prescriptions(patient_id: Optional[int] = None, doctor_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "PATIENT":
        patient_id = current_user.userid
    prescriptions = prescription_service.get_prescriptions(db, current_user, patient_id=patient_id, doctor_id=doctor_id)
    result = []
    for p in prescriptions:
        p_out = PrescriptionOut.model_validate(p)
        p_out.items = prescription_service.get_prescription_items(db, p.prescription_id)
        result.append(p_out)
    return result

@router.post("/", response_model=PrescriptionOut, status_code=status.HTTP_201_CREATED)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    doctor_id = current_user.userid
    new_prescription = prescription_service.create_prescription(db, prescription, doctor_id=doctor_id)
    items = prescription_service.get_prescription_items(db, new_prescription.prescription_id)
    result = PrescriptionOut.model_validate(new_prescription)
    result.items = items
    return result

@router.get("/{prescription_id}", response_model=PrescriptionOut)
def read_prescription(prescription_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_prescription = prescription_service.get_prescription(db, prescription_id)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
        
    if current_user.role == "PATIENT" and db_prescription.patient_id != current_user.userid:
        raise HTTPException(status_code=403, detail="Not authorized to view this prescription")
    if current_user.role == "CAREGIVER":
        caregivers = patient_service.get_caregivers_for_patient(db, db_prescription.patient_id)
        if not any(c.caregiver_id == current_user.userid for c in caregivers):
            raise HTTPException(status_code=403, detail="Not authorized for this patient")
        
    # We should populate items for the output. Since we defined relationship in models, SQLAlchemy can lazy load.
    # Wait, we haven't defined SQLAlchemy relationships explicitly using relationship(), so we'll fetch them.
    # To keep it simple, we can fetch items and assign them to a dictionary or Pydantic will construct it if relationships are mapped.
    # Let's map items manually if relationships are missing in model.
    items = prescription_service.get_prescription_items(db, prescription_id)
    result = PrescriptionOut.model_validate(db_prescription)
    result.items = items
    return result

@router.put("/{prescription_id}", response_model=PrescriptionOut)
def update_prescription(prescription_id: int, prescription_update: PrescriptionUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    db_prescription = prescription_service.get_prescription(db, prescription_id)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
        
    # DOCTORS have global access to update prescriptions
        
    updated = prescription_service.update_prescription(db, prescription_id, prescription_update)
    items = prescription_service.get_prescription_items(db, prescription_id)
    result = PrescriptionOut.model_validate(updated)
    result.items = items
    return result

@router.delete("/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    prescription_service.delete_prescription(db, prescription_id)
    return

@router.delete("/items/{prescription_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prescription_item(prescription_item_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    prescription_service.delete_prescription_item(db, prescription_item_id)
    return
