from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.dispense_schedule import DispenseSchedule
from backend.schemas.schedule import DispenseScheduleCreate, DispenseScheduleUpdate

def get_schedules(db: Session, prescription_item_id: int = None):
    query = db.query(DispenseSchedule)
    if prescription_item_id:
        query = query.filter(DispenseSchedule.prescription_item_id == prescription_item_id)
    return query.all()

def get_schedule(db: Session, schedule_id: int):
    return db.query(DispenseSchedule).filter(DispenseSchedule.schedule_id == schedule_id).first()

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
