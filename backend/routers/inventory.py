from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.schemas.inventory import InventoryCreate, InventoryOut, InventoryUpdate, MedicineBatchCreate, MedicineBatchOut
from backend.services import inventory_service
from backend.auth.dependencies import get_current_user, require_role
from backend.models.user import User

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/", response_model=List[InventoryOut])
def read_inventory(medicine_id: Optional[int] = None, low_stock: bool = False, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR", "CAREGIVER"))):
    return inventory_service.get_inventory_items(db, medicine_id=medicine_id, low_stock_only=low_stock)

@router.post("/", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
def create_inventory(item: InventoryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    return inventory_service.create_inventory_item(db, item)

@router.post("/batch", response_model=MedicineBatchOut, status_code=status.HTTP_201_CREATED)
def create_batch(batch: MedicineBatchCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    return inventory_service.create_medicine_batch(db, batch)

@router.get("/{inventory_id}", response_model=InventoryOut)
def read_inventory_item(inventory_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = inventory_service.get_inventory_item(db, inventory_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_item

@router.put("/{inventory_id}", response_model=InventoryOut)
def update_inventory(inventory_id: int, item_update: InventoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("DOCTOR"))):
    return inventory_service.update_inventory_item(db, inventory_id, item_update)
