from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.prescription import Prescription
from backend.models.prescription_item import PrescriptionItem
from backend.models.dispense_schedule import DispenseSchedule
from backend.schemas.prescription import PrescriptionCreate, PrescriptionUpdate
from datetime import date, time
import re

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
        db.flush() # Get new_item.prescription_item_id
        
        schedule_times = []
        if getattr(item, 'schedule_times', None):
            for t_str in item.schedule_times:
                # expecting t_str like "08:00"
                try:
                    parts = t_str.split(':')
                    schedule_times.append(time(int(parts[0]), int(parts[1])))
                except:
                    pass
        else:
            freq_str = str(item.frequency).lower()
            match = re.search(r'(\d+)', freq_str)
            times_per_day = int(match.group(1)) if match else 1
            times_per_day = min(max(times_per_day, 1), 4)
            
            if times_per_day == 1:
                schedule_times = [time(8, 0)]
            elif times_per_day == 2:
                schedule_times = [time(8, 0), time(20, 0)]
            elif times_per_day == 3:
                schedule_times = [time(8, 0), time(14, 0), time(20, 0)]
            else:
                schedule_times = [time(8, 0), time(12, 0), time(16, 0), time(20, 0)]
            
        for t in schedule_times:
            sched = DispenseSchedule(
                prescription_item_id=new_item.prescription_item_id,
                scheduled_time=t,
                quantity_to_dispense=1,
                start_date=new_prescription.start_date,
                end_date=new_prescription.end_date
            )
            db.add(sched)
    
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

def delete_prescription(db: Session, prescription_id: int):
    db_prescription = get_prescription(db, prescription_id)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Due to cascading foreign keys, deleting items should delete schedules.
    # We delete items first to be safe.
    db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == prescription_id).delete()
    db.delete(db_prescription)
    db.commit()
    return True

def delete_prescription_item(db: Session, prescription_item_id: int):
    item = db.query(PrescriptionItem).filter(PrescriptionItem.prescription_item_id == prescription_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Prescription Item not found")
        
    prescription_id = item.prescription_id
    db.delete(item)
    db.commit()
    
    # Optionally, if it was the last item in the prescription, we could delete the prescription itself.
    remaining = db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == prescription_id).count()
    if remaining == 0:
        db_prescription = get_prescription(db, prescription_id)
        if db_prescription:
            db.delete(db_prescription)
            db.commit()
            
    return True
