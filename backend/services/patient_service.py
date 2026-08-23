from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.patient import Patient
from backend.models.caregiver import CaregiverPatient
from backend.schemas.patient import PatientUpdate
from backend.models.user import User

def get_patients(db: Session, current_user: User):
    query = db.query(Patient, User).join(User, Patient.userid == User.userid)
    if current_user.role == "CAREGIVER":
        query = query.join(CaregiverPatient, Patient.userid == CaregiverPatient.patient_id).filter(CaregiverPatient.caregiver_id == current_user.userid)
    results = query.all()
    out = []
    for p, u in results:
        data = {
            "userid": p.userid,
            "date_of_birth": p.date_of_birth,
            "gender": p.gender,
            "street": p.street,
            "city": p.city,
            "state": p.state,
            "postal_code": p.postal_code,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "role": u.role
        }
        out.append(data)
    return out

def get_patient(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.userid == patient_id).first()

def update_patient(db: Session, patient_id: int, patient_update: PatientUpdate):
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    update_data = patient_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)
        
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_caregivers_for_patient(db: Session, patient_id: int):
    return db.query(CaregiverPatient).filter(CaregiverPatient.patient_id == patient_id).all()
