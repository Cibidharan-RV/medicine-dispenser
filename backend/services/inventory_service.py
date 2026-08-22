from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.inventory import Inventory
from backend.models.medicine_batch import MedicineBatch
from backend.schemas.inventory import InventoryCreate, InventoryUpdate, MedicineBatchCreate

def get_inventory_items(db: Session, medicine_id: int = None, low_stock_only: bool = False):
    query = db.query(Inventory)
    if medicine_id:
        query = query.filter(Inventory.medicine_id == medicine_id)
    if low_stock_only:
        query = query.filter(Inventory.quantity_available < Inventory.minimum_stock_level)
    return query.all()

def get_inventory_item(db: Session, inventory_id: int):
    return db.query(Inventory).filter(Inventory.inventory_id == inventory_id).first()

def create_medicine_batch(db: Session, batch: MedicineBatchCreate):
    new_batch = MedicineBatch(
        batch_number=batch.batch_number,
        medicine_id=batch.medicine_id,
        expiry_date=batch.expiry_date
    )
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch

def create_inventory_item(db: Session, item: InventoryCreate):
    new_item = Inventory(
        medicine_id=item.medicine_id,
        batch_number=item.batch_number,
        quantity_available=item.quantity_available,
        minimum_stock_level=item.minimum_stock_level
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def update_inventory_item(db: Session, inventory_id: int, item_update: InventoryUpdate):
    db_item = get_inventory_item(db, inventory_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
        
    db.commit()
    db.refresh(db_item)
    return db_item
