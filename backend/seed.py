import json
from datetime import date
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models.user import User
from backend.models.patient import Patient
from backend.models.doctor import Doctor
from backend.models.caregiver import Caregiver, CaregiverPatient
from backend.models.medicine import Medicine
from backend.models.dispenser_slot import DispenserSlot
from backend.models.nfc_card import NfcCard
from backend.auth.security import get_password_hash

def seed_db():
    print("Starting database seed process for PostgreSQL...")
    
    db = SessionLocal()
        
    with open("backend/fixtures.json") as f:
        data = json.load(f)
        
    db = SessionLocal()
    
    try:
        # Seed Users
        print("Seeding users...")
        for u in data.get("users", []):
            existing = db.query(User).filter(User.username == u["username"]).first()
            if not existing:
                new_user = User(
                    username=u["username"],
                    hashed_password=get_password_hash(u["password"]),
                    role=u["role"],
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    phone_number=u.get("phone_number")
                )
                db.add(new_user)
                db.flush()
                
                if new_user.role == "DOCTOR":
                    db.add(Doctor(
                        userid=new_user.userid,
                        medical_registration_number=f"DOC-{new_user.userid}",
                        specialization="General Practice"
                    ))
                elif new_user.role == "PATIENT":
                    db.add(Patient(
                        userid=new_user.userid,
                        date_of_birth=date(1980, 1, 1),
                        gender="Male"
                    ))
                elif new_user.role == "CAREGIVER":
                    db.add(Caregiver(userid=new_user.userid))

                if "nfc_uid" in u:
                    db.add(NfcCard(
                        userid=new_user.userid,
                        nfc_uid=u["nfc_uid"]
                    ))
        
        # Seed Medicines
        print("Seeding medicines...")
        for m in data.get("medicines", []):
            existing = db.query(Medicine).filter(Medicine.medicine_name == m["medicine_name"]).first()
            if not existing:
                db.add(Medicine(**m))
                
        # Seed Dispenser Slots
        print("Seeding dispenser slots...")
        for s in data.get("dispenser_slots", []):
            existing = db.query(DispenserSlot).filter(DispenserSlot.slot_number == s["slot_number"]).first()
            if not existing:
                db.add(DispenserSlot(**s))

        db.commit()
        print("Database seeding completed successfully.")
        
        # Link Caregiver to Patient
        caregiver = db.query(User).filter(User.username == "caregiver1").first()
        patient = db.query(User).filter(User.username == "patient1").first()
        if caregiver and patient:
            existing_link = db.query(CaregiverPatient).filter(CaregiverPatient.caregiver_id == caregiver.userid).first()
            if not existing_link:
                db.add(CaregiverPatient(caregiver_id=caregiver.userid, patient_id=patient.userid, relationship_to_patient="Spouse"))
                db.commit()
                print("Caregiver linked to patient.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
