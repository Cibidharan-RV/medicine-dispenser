import pytest
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from backend.models.medicine import Medicine
from backend.models.user import User
from backend.models.patient import Patient
from backend.models.doctor import Doctor
from backend.models.prescription import Prescription
from backend.models.prescription_item import PrescriptionItem
from backend.models.dispense_schedule import DispenseSchedule
from backend.models.medicine_batch import MedicineBatch
from backend.models.inventory import Inventory
from backend.models.dispenser_slot import DispenserSlot
from backend.models.inventory_slot import InventorySlot
from backend.auth.security import get_password_hash

def setup_dispensing_data(db_session):
    # Create doctor and patient
    doctor_user = User(username="doc1", hashed_password=get_password_hash("pass"), role="DOCTOR", first_name="Doc", last_name="Tor")
    patient_user = User(username="pat1", hashed_password=get_password_hash("pass"), role="PATIENT", first_name="Pat", last_name="Ient")
    db_session.add_all([doctor_user, patient_user])
    db_session.commit()
    
    doc = Doctor(userid=doctor_user.userid, medical_registration_number="MRN123", specialization="General")
    pat = Patient(userid=patient_user.userid, date_of_birth=date(1990, 1, 1))
    db_session.add_all([doc, pat])
    db_session.commit()

    # Create medicine
    med = Medicine(medicine_name="TestMed", strength="500mg", dosage_form="Tablet")
    db_session.add(med)
    db_session.commit()

    # Create prescription and item
    current_date = datetime.now().date()
    presc = Prescription(patient_id=pat.userid, doctor_id=doc.userid, prescription_date=current_date, start_date=current_date, end_date=current_date + timedelta(days=10))
    db_session.add(presc)
    db_session.commit()
    
    p_item = PrescriptionItem(prescription_id=presc.prescription_id, medicine_id=med.medicine_id, dosage="1 tab", frequency="Daily", duration="10 days")
    db_session.add(p_item)
    db_session.commit()
    
    # Create schedule
    sched = DispenseSchedule(prescription_item_id=p_item.prescription_item_id, scheduled_time=datetime.now().time(), quantity_to_dispense=1, start_date=current_date, end_date=current_date + timedelta(days=10))
    db_session.add(sched)
    db_session.commit()
    
    # Create batch and inventory
    batch = MedicineBatch(batch_number="B1", medicine_id=med.medicine_id, expiry_date=current_date + timedelta(days=30))
    db_session.add(batch)
    db_session.commit()
    
    inv = Inventory(medicine_id=med.medicine_id, batch_number="B1", quantity_available=10, minimum_stock_level=5)
    db_session.add(inv)
    db_session.commit()
    
    # Assign to slot
    slot = DispenserSlot(slot_number=1, capacity=50)
    db_session.add(slot)
    db_session.commit()
    
    inv_slot = InventorySlot(inventory_id=inv.inventory_id, slot_id=slot.slot_id)
    db_session.add(inv_slot)
    db_session.commit()
    
    return {
        "schedule_id": sched.schedule_id,
        "inventory_id": inv.inventory_id,
        "medicine_id": med.medicine_id
    }

def test_dispensing_logic(client: TestClient, db_session):
    data = setup_dispensing_data(db_session)
    
    # View due schedules
    res = client.get("/api/v1/dispensing/due")
    assert res.status_code == 200
    due_schedules = res.json()
    assert len(due_schedules) > 0
    assert any(s["schedule_id"] == data["schedule_id"] for s in due_schedules)
    
    # Dispense (First time success)
    res = client.post("/api/v1/dispensing/dispense", json={"schedule_id": data["schedule_id"]})
    assert res.status_code == 200
    dispense_result = res.json()
    assert dispense_result["status"] == "SUCCESS"
    assert dispense_result["quantity_dispensed"] == 1
    assert dispense_result["low_stock_warning"] is False
    
    # Check inventory decrement
    inv = db_session.query(Inventory).filter_by(inventory_id=data["inventory_id"]).first()
    assert inv.quantity_available == 9
    
    # Attempt duplicate dispense (Should fail)
    res_dup = client.post("/api/v1/dispensing/dispense", json={"schedule_id": data["schedule_id"]})
    assert res_dup.status_code == 400
    assert "already dispensed" in res_dup.json()["detail"].lower()

def test_minimum_stock_detection(client: TestClient, db_session):
    data = setup_dispensing_data(db_session)
    
    # Set inventory strictly just above minimum stock level so next dispense triggers it
    inv = db_session.query(Inventory).filter_by(inventory_id=data["inventory_id"]).first()
    inv.quantity_available = 5 # Minimum is 5. Dispensing 1 will bring it to 4.
    db_session.commit()
    
    res = client.post("/api/v1/dispensing/dispense", json={"schedule_id": data["schedule_id"]})
    assert res.status_code == 200
    assert res.json()["low_stock_warning"] is True
