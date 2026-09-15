from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.dispense_schedule import DispenseSchedule
from backend.schemas.schedule import DispenseScheduleCreate, DispenseScheduleUpdate

from backend.models.user import User
from backend.models.caregiver import CaregiverPatient
from backend.models.prescription_item import PrescriptionItem
from backend.models.prescription import Prescription

def get_schedules(db: Session, current_user: User, prescription_item_id: int = None):
    query = db.query(DispenseSchedule)
    
    if current_user.role == "PATIENT":
        query = query.join(PrescriptionItem, DispenseSchedule.prescription_item_id == PrescriptionItem.prescription_item_id).join(Prescription, PrescriptionItem.prescription_id == Prescription.prescription_id).filter(Prescription.patient_id == current_user.userid)
    elif current_user.role == "CAREGIVER":
        query = query.join(PrescriptionItem, DispenseSchedule.prescription_item_id == PrescriptionItem.prescription_item_id).join(Prescription, PrescriptionItem.prescription_id == Prescription.prescription_id).join(CaregiverPatient, Prescription.patient_id == CaregiverPatient.patient_id).filter(CaregiverPatient.caregiver_id == current_user.userid)
        
    if prescription_item_id:
        query = query.filter(DispenseSchedule.prescription_item_id == prescription_item_id)
    return query.all()

def get_schedule(db: Session, current_user: User, schedule_id: int):
    query = db.query(DispenseSchedule).filter(DispenseSchedule.schedule_id == schedule_id)
    
    if current_user.role == "PATIENT":
        query = query.join(PrescriptionItem, DispenseSchedule.prescription_item_id == PrescriptionItem.prescription_item_id).join(Prescription, PrescriptionItem.prescription_id == Prescription.prescription_id).filter(Prescription.patient_id == current_user.userid)
    elif current_user.role == "CAREGIVER":
        query = query.join(PrescriptionItem, DispenseSchedule.prescription_item_id == PrescriptionItem.prescription_item_id).join(Prescription, PrescriptionItem.prescription_id == Prescription.prescription_id).join(CaregiverPatient, Prescription.patient_id == CaregiverPatient.patient_id).filter(CaregiverPatient.caregiver_id == current_user.userid)
        
    return query.first()

def create_schedule(db: Session, schedule: DispenseScheduleCreate):
    new_schedule = DispenseSchedule(
        prescription_item_id=schedule.prescription_item_id,
        scheduled_time=schedule.scheduled_time,
        quantity_to_dispense=schedule.quantity_to_dispense,
        start_date=schedule.start_date,
        end_date=schedule.end_date
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule

def update_schedule(db: Session, schedule_id: int, schedule_update: DispenseScheduleUpdate):
    db_schedule = get_schedule(db, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    update_data = schedule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
        
    db.commit()
    db.refresh(db_schedule)
    return db_schedule
