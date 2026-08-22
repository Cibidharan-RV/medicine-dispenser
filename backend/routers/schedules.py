from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.schemas.schedule import DispenseScheduleCreate, DispenseScheduleOut, DispenseScheduleUpdate
from backend.services import schedule_service
from backend.auth.dependencies import get_current_user, require_role
from backend.models.user import User

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.get("/", response_model=List[DispenseScheduleOut])
def read_schedules(prescription_item_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # In a real app we'd check if the PATIENT owns the prescription_item_id
    return schedule_service.get_schedules(db, prescription_item_id=prescription_item_id)

@router.post("/", response_model=DispenseScheduleOut, status_code=status.HTTP_201_CREATED)
def create_schedule(schedule: DispenseScheduleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    return schedule_service.create_schedule(db, schedule)

@router.get("/{schedule_id}", response_model=DispenseScheduleOut)
def read_schedule(schedule_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_schedule = schedule_service.get_schedule(db, schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

@router.put("/{schedule_id}", response_model=DispenseScheduleOut)
def update_schedule(schedule_id: int, schedule_update: DispenseScheduleUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    return schedule_service.update_schedule(db, schedule_id, schedule_update)
