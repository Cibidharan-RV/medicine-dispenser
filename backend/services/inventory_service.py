from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.inventory import Inventory
from backend.models.medicine_batch import MedicineBatch
from backend.schemas.inventory import InventoryCreate, InventoryUpdate, MedicineBatchCreate

def get_inventory_items(db: Session, medicine_id: int = None, low_stock_only: bool = False):
    query = db.query(Inventory, MedicineBatch.expiry_date).outerjoin(
        MedicineBatch, 
        (Inventory.medicine_id == MedicineBatch.medicine_id) & (Inventory.batch_number == MedicineBatch.batch_number)
    )
    if medicine_id:
        query = query.filter(Inventory.medicine_id == medicine_id)
    if low_stock_only:
        query = query.filter(Inventory.quantity_available < Inventory.minimum_stock_level)
        
    results = []
    for inv, exp_date in query.all():
        data = {
            "inventory_id": inv.inventory_id,
            "medicine_id": inv.medicine_id,
            "batch_number": inv.batch_number,
            "quantity_available": inv.quantity_available,
            "minimum_stock_level": inv.minimum_stock_level,
            "expiry_date": exp_date
        }
        results.append(data)
    return results

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

from backend.schemas.inventory import TopUpRequest
from datetime import date

def process_topup(db: Session, topup: TopUpRequest):
    batch_num = f"MED-{topup.medicine_id}-EXP-{topup.expiry_month:02d}-{topup.expiry_year}"
    
    # Check or create batch
    batch = db.query(MedicineBatch).filter(
        MedicineBatch.medicine_id == topup.medicine_id,
        MedicineBatch.batch_number == batch_num
    ).first()
    
    if not batch:
        expiry_date = date(topup.expiry_year, topup.expiry_month, 1)
        batch = MedicineBatch(
            batch_number=batch_num,
            medicine_id=topup.medicine_id,
            expiry_date=expiry_date
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        
    # Check or create inventory
    inv = db.query(Inventory).filter(
        Inventory.medicine_id == topup.medicine_id,
        Inventory.batch_number == batch_num
    ).first()
    
    if not inv:
        inv = Inventory(
            medicine_id=topup.medicine_id,
            batch_number=batch_num,
            quantity_available=topup.quantity_to_add,
            minimum_stock_level=topup.minimum_stock_level
        )
        db.add(inv)
    else:
        inv.quantity_available += topup.quantity_to_add
        if topup.minimum_stock_level is not None:
            inv.minimum_stock_level = topup.minimum_stock_level
            
    db.commit()
    db.refresh(inv)
    return inv
