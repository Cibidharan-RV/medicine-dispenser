from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.prescription import Prescription
from backend.models.prescription_item import PrescriptionItem
from backend.schemas.prescription import PrescriptionCreate, PrescriptionUpdate
from datetime import date

from backend.models.user import User
from backend.models.caregiver import CaregiverPatient

def get_prescriptions(db: Session, current_user: User, patient_id: int = None, doctor_id: int = None):
    query = db.query(Prescription)
    
    if current_user.role == "CAREGIVER":
        query = query.join(CaregiverPatient, Prescription.patient_id == CaregiverPatient.patient_id).filter(CaregiverPatient.caregiver_id == current_user.userid)
        
    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Prescription.doctor_id == doctor_id)
    return query.all()

def get_prescription(db: Session, prescription_id: int):
    return db.query(Prescription).filter(Prescription.prescription_id == prescription_id).first()

def create_prescription(db: Session, prescription: PrescriptionCreate, doctor_id: int):
    new_prescription = Prescription(
        patient_id=prescription.patient_id,
        doctor_id=doctor_id,
        prescription_date=prescription.prescription_date,
        start_date=prescription.start_date,
        end_date=prescription.end_date
    )
    db.add(new_prescription)
    db.flush() # Get prescription_id

    for item in prescription.items:
        new_item = PrescriptionItem(
            prescription_id=new_prescription.prescription_id,
            medicine_id=item.medicine_id,
            dosage=item.dosage,
            frequency=item.frequency,
            duration=item.duration
        )
        db.add(new_item)
    
    db.commit()
    db.refresh(new_prescription)
    return new_prescription

def update_prescription(db: Session, prescription_id: int, prescription_update: PrescriptionUpdate):
    db_prescription = get_prescription(db, prescription_id)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    if prescription_update.end_date is not None:
        db_prescription.end_date = prescription_update.end_date
        
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def get_prescription_items(db: Session, prescription_id: int):
    return db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == prescription_id).all()
