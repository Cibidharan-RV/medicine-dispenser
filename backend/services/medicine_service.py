from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.medicine import Medicine
from backend.schemas.medicine import MedicineCreate, MedicineUpdate

def get_medicines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Medicine).offset(skip).limit(limit).all()

def get_medicine(db: Session, medicine_id: int):
    return db.query(Medicine).filter(Medicine.medicine_id == medicine_id).first()

def create_medicine(db: Session, medicine: MedicineCreate):
    db_medicine = Medicine(
        medicine_name=medicine.medicine_name,
        strength=medicine.strength,
        dosage_form=medicine.dosage_form,
        manufacturer=medicine.manufacturer
    )
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def update_medicine(db: Session, medicine_id: int, medicine_update: MedicineUpdate):
    db_medicine = get_medicine(db, medicine_id)
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    update_data = medicine_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_medicine, key, value)
        
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def delete_medicine(db: Session, medicine_id: int):
    db_medicine = get_medicine(db, medicine_id)
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
        
    try:
        db.delete(db_medicine)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Cannot delete medicine because it is referenced by other records")
    return db_medicine
