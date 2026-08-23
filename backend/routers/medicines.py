from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.medicine import MedicineCreate, MedicineOut, MedicineUpdate
from backend.services import medicine_service
from backend.auth.dependencies import require_role

router = APIRouter(prefix="/medicines", tags=["medicines"])

@router.get("/", response_model=List[MedicineOut])
def read_medicines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return medicine_service.get_medicines(db, skip=skip, limit=limit)

@router.get("/{medicine_id}", response_model=MedicineOut)
def read_medicine(medicine_id: int, db: Session = Depends(get_db)):
    db_medicine = medicine_service.get_medicine(db, medicine_id)
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return db_medicine

@router.post("/", response_model=MedicineOut, status_code=status.HTTP_201_CREATED)
def create_medicine(medicine: MedicineCreate, db: Session = Depends(get_db), _ = Depends(require_role("DOCTOR"))):
    return medicine_service.create_medicine(db, medicine)

@router.put("/{medicine_id}", response_model=MedicineOut)
def update_medicine(medicine_id: int, medicine_update: MedicineUpdate, db: Session = Depends(get_db), _ = Depends(require_role("DOCTOR"))):
    return medicine_service.update_medicine(db, medicine_id, medicine_update)

@router.delete("/{medicine_id}")
def delete_medicine(medicine_id: int, db: Session = Depends(get_db), _ = Depends(require_role("DOCTOR"))):
    medicine_service.delete_medicine(db, medicine_id)
    return {"ok": True}
