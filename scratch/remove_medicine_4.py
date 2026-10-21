from sqlalchemy.orm import Session
from backend.database import engine
from backend.models.dispense_schedule import DispenseSchedule
from backend.models.prescription_item import PrescriptionItem

def remove_medicine4():
    with Session(engine) as db:
        items = db.query(PrescriptionItem).filter(PrescriptionItem.medicine_id == 4).all()
        for item in items:
            # Delete related schedules
            db.query(DispenseSchedule).filter(DispenseSchedule.prescription_item_id == item.prescription_item_id).delete()
            db.delete(item)
        db.commit()
        print("Successfully removed Medicine 4 (Ibuprofen) from the prescription schedule.")

if __name__ == "__main__":
    remove_medicine4()
