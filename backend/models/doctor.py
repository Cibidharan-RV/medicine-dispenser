from sqlalchemy import Column, BigInteger, String, ForeignKey
from backend.database import Base

class Doctor(Base):
    __tablename__ = "doctor"

    userid = Column("userid", BigInteger, ForeignKey("USER.userid", ondelete="CASCADE"), primary_key=True)
    medical_registration_number = Column("medicalregistrationnumber", String(50), unique=True, nullable=False)
    specialization = Column("specialization", String(100), nullable=False)
