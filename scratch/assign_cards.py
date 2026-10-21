import sys
import os
from sqlalchemy.orm import Session
from backend.database import engine
from backend.models.user import User
from backend.models.nfc_card import NfcCard

def assign_cards(patient_username, patient_uid, caregiver_username, caregiver_uid):
    with Session(engine) as db:
        # Assign for patient
        patient = db.query(User).filter(User.username == patient_username).first()
        if patient:
            # Check if card exists
            existing_card = db.query(NfcCard).filter(NfcCard.userid == patient.userid).first()
            if existing_card:
                existing_card.nfc_uid = patient_uid
                print(f"Updated card for {patient_username} to {patient_uid}")
            else:
                db.add(NfcCard(userid=patient.userid, nfc_uid=patient_uid))
                print(f"Assigned new card to {patient_username}: {patient_uid}")
        else:
            print(f"User {patient_username} not found")

        # Assign for caregiver
        caregiver = db.query(User).filter(User.username == caregiver_username).first()
        if caregiver:
            existing_card = db.query(NfcCard).filter(NfcCard.userid == caregiver.userid).first()
            if existing_card:
                existing_card.nfc_uid = caregiver_uid
                print(f"Updated card for {caregiver_username} to {caregiver_uid}")
            else:
                db.add(NfcCard(userid=caregiver.userid, nfc_uid=caregiver_uid))
                print(f"Assigned new card to {caregiver_username}: {caregiver_uid}")
        else:
            print(f"User {caregiver_username} not found")

        db.commit()
        print("Done!")

if __name__ == "__main__":
    print("Please enter the NFC UID for Patient 1 (e.g. A1:B2:C3:D4):")
    patient_uid = input("> ").strip()
    
    print("Please enter the NFC UID for Caregiver 1 (e.g. E5:F6:A7:B8):")
    caregiver_uid = input("> ").strip()
    
    assign_cards("patient1", patient_uid, "caregiver1", caregiver_uid)
