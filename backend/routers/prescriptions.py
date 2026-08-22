from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.schemas.prescription import PrescriptionCreate, PrescriptionOut, PrescriptionUpdate, PrescriptionItemOut
from backend.services import prescription_service
from backend.auth.dependencies import get_current_user, require_role
from backend.models.user import User

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

@router.get("/", response_model=List[PrescriptionOut])
def read_prescriptions(patient_id: Optional[int] = None, doctor_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # PATIENT can only see their own prescriptions
    if current_user.role == "PATIENT":
        patient_id = current_user.userid
    # DOCTOR can optionally filter by their own or patients
    if current_user.role == "DOCTOR" and doctor_id is None:
        doctor_id = current_user.userid
        
    return prescription_service.get_prescriptions(db, patient_id=patient_id, doctor_id=doctor_id)

@router.post("/", response_model=PrescriptionOut, status_code=status.HTTP_201_CREATED)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    doctor_id = current_user.userid
    return prescription_service.create_prescription(db, prescription, doctor_id=doctor_id)

@router.get("/{prescription_id}", response_model=PrescriptionOut)
def read_prescription(prescription_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_prescription = prescription_service.get_prescription(db, prescription_id)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
        
    if current_user.role == "PATIENT" and db_prescription.patient_id != current_user.userid:
        raise HTTPException(status_code=403, detail="Not authorized to view this prescription")
    if current_user.role == "DOCTOR" and db_prescription.doctor_id != current_user.userid:
        raise HTTPException(status_code=403, detail="Not authorized to view this prescription")
        
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
        
    if current_user.role == "DOCTOR" and db_prescription.doctor_id != current_user.userid:
        raise HTTPException(status_code=403, detail="Not authorized to update this prescription")
        
    updated = prescription_service.update_prescription(db, prescription_id, prescription_update)
    items = prescription_service.get_prescription_items(db, prescription_id)
    result = PrescriptionOut.model_validate(updated)
    result.items = items
    return result
