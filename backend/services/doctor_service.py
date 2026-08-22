from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.doctor import Doctor
from backend.schemas.doctor import DoctorUpdate

def get_doctors(db: Session):
    return db.query(Doctor).all()

def get_doctor(db: Session, doctor_id: int):
    return db.query(Doctor).filter(Doctor.userid == doctor_id).first()

def update_doctor(db: Session, doctor_id: int, doctor_update: DoctorUpdate):
    db_doctor = get_doctor(db, doctor_id)
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    update_data = doctor_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_doctor, key, value)
        
    db.commit()
    db.refresh(db_doctor)
    return db_doctor
