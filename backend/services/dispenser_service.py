from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.dispenser_slot import DispenserSlot
from backend.models.inventory_slot import InventorySlot
from backend.schemas.dispenser import DispenserSlotCreate, DispenserSlotUpdate, InventorySlotCreate

def get_slots(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DispenserSlot).offset(skip).limit(limit).all()

def get_slot(db: Session, slot_id: int):
    return db.query(DispenserSlot).filter(DispenserSlot.slot_id == slot_id).first()

def get_slot_by_number(db: Session, slot_number: int):
    return db.query(DispenserSlot).filter(DispenserSlot.slot_number == slot_number).first()

def create_slot(db: Session, slot: DispenserSlotCreate):
    if get_slot_by_number(db, slot.slot_number):
        raise HTTPException(status_code=409, detail="Slot number already exists")
    db_slot = DispenserSlot(
        slot_number=slot.slot_number,
        capacity=slot.capacity
    )
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

def update_slot(db: Session, slot_id: int, slot_update: DispenserSlotUpdate):
    db_slot = get_slot(db, slot_id)
    if not db_slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    if slot_update.capacity is not None:
        db_slot.capacity = slot_update.capacity
        
    db.commit()
    db.refresh(db_slot)
    return db_slot

def assign_inventory_to_slot(db: Session, mapping: InventorySlotCreate):
    # Check if slot exists
    if not get_slot(db, mapping.slot_id):
        raise HTTPException(status_code=404, detail="Slot not found")
        
    # Check if inventory or slot already mapped (using constraint/query)
    existing_by_inv = db.query(InventorySlot).filter(InventorySlot.inventory_id == mapping.inventory_id).first()
    existing_by_slot = db.query(InventorySlot).filter(InventorySlot.slot_id == mapping.slot_id).first()
    
    if existing_by_inv:
        raise HTTPException(status_code=409, detail="Inventory is already assigned to a slot")
    if existing_by_slot:
        raise HTTPException(status_code=409, detail="Slot is already assigned to an inventory")
        
    db_mapping = InventorySlot(
        inventory_id=mapping.inventory_id,
        slot_id=mapping.slot_id
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

def get_slot_assignment(db: Session, inventory_id: int):
    return db.query(InventorySlot).filter(InventorySlot.inventory_id == inventory_id).first()
