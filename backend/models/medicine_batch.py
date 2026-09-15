from sqlalchemy import Column, BigInteger, String, Date, ForeignKey
from backend.database import Base

class MedicineBatch(Base):
    __tablename__ = "medicine_batch"

    batch_number = Column("batchnumber", String(100), primary_key=True)
    medicine_id = Column("medicineid", BigInteger, ForeignKey("medicine.medicineid", ondelete="CASCADE"), primary_key=True)
    expiry_date = Column("expirydate", Date, nullable=False)
