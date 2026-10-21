from backend.database import SessionLocal
from backend.models.user import User

db = SessionLocal()
# Find first patient
patient = db.query(User).filter(User.role == "PATIENT").first()

from sqlalchemy import text

if patient:
    # Insert raw SQL to seed the NFC card since we don't have the SQLAlchemy model yet
    db.execute(
        text("INSERT INTO nfc_cards (userid, nfc_uid) VALUES (:userid, :nfc_uid) ON CONFLICT (nfc_uid) DO NOTHING"),
        {"userid": patient.userid, "nfc_uid": "test-patient-card-1234"}
    )
    db.commit()
    print(f"Seeded NFC card 'test-patient-card-1234' for PATIENT userid={patient.userid} ({patient.username})")
else:
    print("No patient found!")
db.close()
