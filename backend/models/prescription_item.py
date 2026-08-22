from sqlalchemy import Column, BigInteger, String, ForeignKey
from backend.database import Base

class PrescriptionItem(Base):
    __tablename__ = "PRESCRIPTION_ITEM"

    prescription_item_id = Column("prescriptionitemid", BigInteger, primary_key=True, index=True)
    prescription_id = Column("prescriptionid", BigInteger, ForeignKey("PRESCRIPTION.prescriptionid", ondelete="CASCADE"), nullable=False)
    medicine_id = Column("medicineid", BigInteger, ForeignKey("MEDICINE.medicineid"), nullable=False)
    dosage = Column("dosage", String(100), nullable=False)
    frequency = Column("frequency", String(100), nullable=False)
    duration = Column("duration", String(100), nullable=False)
