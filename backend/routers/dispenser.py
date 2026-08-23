from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.dispenser import DispenserSlotCreate, DispenserSlotOut, DispenserSlotUpdate, InventorySlotCreate, InventorySlotOut
from backend.services import dispenser_service
from backend.auth.dependencies import require_role
from backend.models.user import User

router = APIRouter(prefix="/dispenser", tags=["dispenser"])

@router.get("/slots", response_model=List[DispenserSlotOut])
def read_slots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    return dispenser_service.get_slots(db, skip=skip, limit=limit)

@router.post("/slots", response_model=DispenserSlotOut, status_code=status.HTTP_201_CREATED)
def create_slot(slot: DispenserSlotCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    return dispenser_service.create_slot(db, slot)

@router.put("/slots/{slot_id}", response_model=DispenserSlotOut)
def update_slot(slot_id: int, slot_update: DispenserSlotUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    return dispenser_service.update_slot(db, slot_id, slot_update)

@router.post("/assign", response_model=InventorySlotOut, status_code=status.HTTP_201_CREATED)
def assign_inventory(mapping: InventorySlotCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    return dispenser_service.assign_inventory_to_slot(db, mapping)

@router.get("/assign/{inventory_id}", response_model=InventorySlotOut)
def get_assignment(inventory_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    assignment = dispenser_service.get_slot_assignment(db, inventory_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment
