from sqlalchemy import Column, BigInteger, String
from backend.database import Base

class Medicine(Base):
    __tablename__ = "MEDICINE"

    medicine_id = Column("medicineid", BigInteger, primary_key=True, index=True)
    medicine_name = Column("medicinename", String(150), nullable=False)
    strength = Column("strength", String(50), nullable=False)
    dosage_form = Column("dosageform", String(50), nullable=False)
    manufacturer = Column("manufacturer", String(150))
