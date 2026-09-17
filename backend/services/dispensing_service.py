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
from backend.models.medicine import Medicine
from backend.schemas.dispense import DispenseRequest

def get_due_schedules(db: Session, target_time: datetime = None, patient_id: int = None):
    if target_time is None:
        target_time = datetime.now()
        
    current_date = target_time.date()
    current_time = target_time.time()
    
    # Simple check: find schedules where the current date is within bounds
    # and the scheduled time is due (let's say within 1 hour before/after or exactly due)
    # For this basic implementation, we just return schedules that are within the active date range.
    
    query = db.query(DispenseSchedule).filter(
        DispenseSchedule.start_date <= current_date,
        DispenseSchedule.end_date >= current_date
    )
    
    if patient_id is not None:
        query = query.join(
            PrescriptionItem, DispenseSchedule.prescription_item_id == PrescriptionItem.prescription_item_id
        ).join(
            Prescription, PrescriptionItem.prescription_id == Prescription.prescription_id
        ).filter(
            Prescription.patient_id == patient_id
        )
        
    active_schedules = query.all()
    
    due_schedules = []
    for schedule in active_schedules:
        # Check if already dispensed successfully today
        already_dispensed = db.query(DispenseLog).filter(
            DispenseLog.schedule_id == schedule.schedule_id,
            func.date(DispenseLog.dispense_datetime) == current_date,
            DispenseLog.status == 'SUCCESS'
        ).first()
        
        if not already_dispensed:
            # Attach medicine_name for frontend convenience
            med = db.query(Medicine).join(
                PrescriptionItem, PrescriptionItem.medicine_id == Medicine.medicine_id
            ).filter(PrescriptionItem.prescription_item_id == schedule.prescription_item_id).first()
            
            if med:
                schedule.medicine_name = med.medicine_name
            due_schedules.append(schedule)
            
    return due_schedules

def dispense(db: Session, request: DispenseRequest):
    schedule = db.query(DispenseSchedule).filter(DispenseSchedule.schedule_id == request.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    current_date = datetime.now().date()
    
    try:
        # Check duplicate
        already_dispensed = db.query(DispenseLog).filter(
            DispenseLog.schedule_id == schedule.schedule_id,
            func.date(DispenseLog.dispense_datetime) == current_date,
            DispenseLog.status == 'SUCCESS'
        ).first()
        
        if already_dispensed:
            raise ValueError("Schedule already dispensed today")
            
        prescription_item = db.query(PrescriptionItem).filter(PrescriptionItem.prescription_item_id == schedule.prescription_item_id).first()
        prescription = db.query(Prescription).filter(Prescription.prescription_id == prescription_item.prescription_id).first()
        
        # Prescription validity
        if not (prescription.start_date <= current_date <= prescription.end_date):
            raise ValueError("Prescription not valid today")
            
        # Find inventory ordered by expiry date (FEFO)
        inventories = db.query(Inventory).join(MedicineBatch, (Inventory.medicine_id == MedicineBatch.medicine_id) & (Inventory.batch_number == MedicineBatch.batch_number)).filter(
            Inventory.medicine_id == prescription_item.medicine_id,
            MedicineBatch.expiry_date >= current_date,
            Inventory.quantity_available > 0
        ).with_for_update().order_by(MedicineBatch.expiry_date.asc()).all()
        
        if not inventories:
            raise ValueError("No valid medicine batch found")
            
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
            raise ValueError("Insufficient inventory or no dispenser slot assigned")
            
        status = "SUCCESS" if required_qty == 0 else "PARTIAL"
        reason = None if status == "SUCCESS" else "Insufficient total valid inventory"
        
        log = DispenseLog(
            schedule_id=schedule.schedule_id,
            dispense_datetime=datetime.now(),
            quantity_dispensed=quantity_dispensed,
            status=status,
            failure_reason=reason
        )
        db.add(log)
        
        db.commit()
        return {
            "log_id": log.dispense_id,
            "quantity_dispensed": quantity_dispensed,
            "status": status,
            "low_stock_warning": low_stock_triggered
        }
        
    except ValueError as e:
        db.rollback()
        
        # Log the failure in a new transaction
        failure_log = DispenseLog(
            schedule_id=schedule.schedule_id,
            dispense_datetime=datetime.now(),
            quantity_dispensed=0,
            status="FAILED",
            failure_reason=str(e)
        )
        db.add(failure_log)
        db.commit()
        
        raise HTTPException(status_code=400, detail=str(e))

def get_dispense_history(db: Session, patient_id: int):
    return db.query(DispenseLog).join(
        DispenseSchedule, DispenseLog.schedule_id == DispenseSchedule.schedule_id
    ).join(
        PrescriptionItem, DispenseSchedule.prescription_item_id == PrescriptionItem.prescription_item_id
    ).join(
        Prescription, PrescriptionItem.prescription_id == Prescription.prescription_id
    ).filter(
        Prescription.patient_id == patient_id
    ).order_by(DispenseLog.dispense_datetime.desc()).all()
