from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import engine
from backend.models.user import User
from backend.models.medicine import Medicine
from backend.models.medicine_batch import MedicineBatch
from backend.models.inventory import Inventory
from backend.models.inventory_slot import InventorySlot
from backend.models.dispenser_slot import DispenserSlot
from backend.models.prescription import Prescription
from backend.models.prescription_item import PrescriptionItem
from backend.models.dispense_schedule import DispenseSchedule

def seed_extra():
    with Session(engine) as db:
        print("Starting extra seeding...")
        # Get patient and doctor
        patient = db.query(User).filter(User.username == 'patient1').first()
        doctor = db.query(User).filter(User.username == 'doctor1').first()

        if not patient or not doctor:
            print("Patient or doctor not found. Make sure you ran seed.py first.")
            return

        # Add more medicines
        med3 = db.query(Medicine).filter(Medicine.medicine_name == 'Amoxicillin').first()
        if not med3:
            med3 = Medicine(medicine_name='Amoxicillin', strength='250mg', dosage_form='Capsule', manufacturer='HealthInc')
            db.add(med3)
            
        med4 = db.query(Medicine).filter(Medicine.medicine_name == 'Ibuprofen').first()
        if not med4:
            med4 = Medicine(medicine_name='Ibuprofen', strength='200mg', dosage_form='Tablet', manufacturer='PharmaCorp')
            db.add(med4)
            
        db.commit()
        
        # Get all 4 medicines
        med1 = db.query(Medicine).filter(Medicine.medicine_name == 'Lisinopril').first()
        med2 = db.query(Medicine).filter(Medicine.medicine_name == 'Metformin').first()
        
        medicines = [med1, med2, med3, med4]
        
        print("Seeding MedicineBatches, Inventory, and Slots...")
        # Add MedicineBatches and Inventory
        expiry = date.today() + timedelta(days=365)
        for i, m in enumerate(medicines, start=1):
            batch = db.query(MedicineBatch).filter(MedicineBatch.medicine_id == m.medicine_id).first()
            if not batch:
                batch = MedicineBatch(medicine_id=m.medicine_id, batch_number=f"BATCH-{i}", expiry_date=expiry)
                db.add(batch)
                db.commit()
            
            inv = db.query(Inventory).filter(Inventory.medicine_id == m.medicine_id).first()
            if not inv:
                inv = Inventory(medicine_id=m.medicine_id, batch_number=f"BATCH-{i}", quantity_available=100, minimum_stock_level=10)
                db.add(inv)
                db.commit()
            
            # Link to slot 1, 2, 3, 4
            slot = db.query(DispenserSlot).filter(DispenserSlot.slot_number == i).first()
            if slot:
                inv_slot = db.query(InventorySlot).filter(InventorySlot.inventory_id == inv.inventory_id).first()
                if not inv_slot:
                    inv_slot = InventorySlot(inventory_id=inv.inventory_id, slot_id=slot.slot_id)
                    db.add(inv_slot)
                    db.commit()
                    
        # Add Prescription
        print("Seeding Prescription...")
        presc = db.query(Prescription).filter(Prescription.patient_id == patient.userid).first()
        if not presc:
            presc = Prescription(
                patient_id=patient.userid,
                doctor_id=doctor.userid,
                prescription_date=date.today(),
                start_date=date.today() - timedelta(days=1),
                end_date=date.today() + timedelta(days=30)
            )
            db.add(presc)
            db.commit()
            db.refresh(presc)
        
        # Add items and schedules
        print("Seeding Prescription Items and Schedules...")
        for m in medicines:
            item = db.query(PrescriptionItem).filter(
                PrescriptionItem.prescription_id == presc.prescription_id, 
                PrescriptionItem.medicine_id == m.medicine_id
            ).first()
            
            if not item:
                item = PrescriptionItem(
                    prescription_id=presc.prescription_id,
                    medicine_id=m.medicine_id,
                    dosage="1 pill",
                    frequency="Daily",
                    duration="30 Days"
                )
                db.add(item)
                db.commit()
                db.refresh(item)
                
            # Add schedule
            sched = db.query(DispenseSchedule).filter(DispenseSchedule.prescription_item_id == item.prescription_item_id).first()
            if not sched:
                sched = DispenseSchedule(
                    prescription_item_id=item.prescription_item_id,
                    scheduled_time=datetime.now().time(), # Due right now!
                    quantity_to_dispense=1,
                    start_date=date.today() - timedelta(days=1),
                    end_date=date.today() + timedelta(days=30)
                )
                db.add(sched)
                db.commit()
                
        print("Extra data seeded successfully!")

if __name__ == "__main__":
    seed_extra()
