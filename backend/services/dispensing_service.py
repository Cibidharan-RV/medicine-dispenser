from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime, date
from backend.models.dispense_schedule import DispenseSchedule
from backend.models.prescription_item import PrescriptionItem
from backend.models.prescription import Prescription
from backend.models.inventory import Inventory
from backend.models.inventory_slot import InventorySlot
from backend.models.dispenser_slot import DispenserSlot
from backend.models.medicine_batch import MedicineBatch
from backend.models.dispense_log import DispenseLog
from backend.schemas.dispense import DispenseRequest

def get_due_schedules(db: Session, target_time: datetime = None):
    if target_time is None:
        target_time = datetime.now()
        
    current_date = target_time.date()
    current_time = target_time.time()
    
    # Simple check: find schedules where the current date is within bounds
    # and the scheduled time is due (let's say within 1 hour before/after or exactly due)
    # For this basic implementation, we just return schedules that are within the active date range.
    
    # Ideally, we would join with DispenseLog to see if it's already dispensed today.
    # We will let the client filter out the ones already dispensed, or we can filter it here.
    
    active_schedules = db.query(DispenseSchedule).filter(
        DispenseSchedule.start_date <= current_date,
        DispenseSchedule.end_date >= current_date
    ).all()
    
    due_schedules = []
    for schedule in active_schedules:
        # Check if already dispensed successfully today
        already_dispensed = db.query(DispenseLog).filter(
            DispenseLog.schedule_id == schedule.schedule_id,
            func.date(DispenseLog.dispense_datetime) == current_date,
            DispenseLog.status == 'SUCCESS'
        ).first()
        
        if not already_dispensed:
            due_schedules.append(schedule)
            
    return due_schedules

def dispense(db: Session, request: DispenseRequest):
    schedule = db.query(DispenseSchedule).filter(DispenseSchedule.schedule_id == request.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    # Check duplicate
    current_date = datetime.now().date()
    already_dispensed = db.query(DispenseLog).filter(
        DispenseLog.schedule_id == schedule.schedule_id,
        func.date(DispenseLog.dispense_datetime) == current_date,
        DispenseLog.status == 'SUCCESS'
    ).first()
    
    if already_dispensed:
        raise HTTPException(status_code=400, detail="Schedule already dispensed today")
        
    prescription_item = db.query(PrescriptionItem).filter(PrescriptionItem.prescription_item_id == schedule.prescription_item_id).first()
    prescription = db.query(Prescription).filter(Prescription.prescription_id == prescription_item.prescription_id).first()
    
    # Prescription validity
    if not (prescription.start_date <= current_date <= prescription.end_date):
        _log_dispense(db, schedule.schedule_id, 0, "FAILED", "Prescription not valid today")
        raise HTTPException(status_code=400, detail="Prescription not valid today")
        
    # Find inventory ordered by expiry date (FEFO)
    inventories = db.query(Inventory).join(MedicineBatch, (Inventory.medicine_id == MedicineBatch.medicine_id) & (Inventory.batch_number == MedicineBatch.batch_number)).filter(
        Inventory.medicine_id == prescription_item.medicine_id,
        MedicineBatch.expiry_date >= current_date,
        Inventory.quantity_available > 0
    ).order_by(MedicineBatch.expiry_date.asc()).all()
    
    if not inventories:
        _log_dispense(db, schedule.schedule_id, 0, "FAILED", "No valid medicine batch found")
        raise HTTPException(status_code=400, detail="No valid medicine batch found")
        
    required_qty = schedule.quantity_to_dispense
    quantity_dispensed = 0
    low_stock_triggered = False
    
    for inv in inventories:
        if required_qty <= 0:
            break
            
        slot = db.query(InventorySlot).filter(InventorySlot.inventory_id == inv.inventory_id).first()
        if not slot:
            continue # Skip inventory not mapped to a slot
            
        dispense_from_this_inv = min(inv.quantity_available, required_qty)
        inv.quantity_available -= dispense_from_this_inv
        required_qty -= dispense_from_this_inv
        quantity_dispensed += dispense_from_this_inv
        
        if inv.quantity_available < inv.minimum_stock_level:
            low_stock_triggered = True
            
    if quantity_dispensed == 0:
        _log_dispense(db, schedule.schedule_id, 0, "FAILED", "Insufficient inventory or no dispenser slot assigned")
        raise HTTPException(status_code=400, detail="Insufficient inventory or no dispenser slot assigned")
        
    status = "SUCCESS" if required_qty == 0 else "PARTIAL"
    reason = None if status == "SUCCESS" else "Insufficient total valid inventory"
    
    log = _log_dispense(db, schedule.schedule_id, quantity_dispensed, status, reason)
    
    db.commit()
    return {
        "log_id": log.dispense_id,
        "quantity_dispensed": quantity_dispensed,
        "status": status,
        "low_stock_warning": low_stock_triggered
    }

def _log_dispense(db: Session, schedule_id: int, qty: int, status: str, reason: str = None):
    log = DispenseLog(
        schedule_id=schedule_id,
        dispense_datetime=datetime.now(),
        quantity_dispensed=qty,
        status=status,
        failure_reason=reason
    )
    db.add(log)
    if status == "FAILED":
        db.commit() # Commit failures individually if part of a bad run
    return log
