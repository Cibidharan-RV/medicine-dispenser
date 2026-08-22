from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend.schemas.schedule import DispenseScheduleOut
from backend.schemas.dispense import DispenseRequest
from backend.services import dispensing_service
from backend.auth.dependencies import get_current_user, require_role
from backend.models.user import User

router = APIRouter(prefix="/dispensing", tags=["dispensing"])

@router.get("/due", response_model=List[DispenseScheduleOut])
def get_due_schedules(db: Session = Depends(get_db)):
    # Hardware ESP32 endpoint. For now, open to allow device polling.
    return dispensing_service.get_due_schedules(db)

@router.post("/dispense")
def dispense(request: DispenseRequest, db: Session = Depends(get_db)):
    # Hardware ESP32 endpoint to log successful physical dispensing, or trigger it
    return dispensing_service.dispense(db, request)
