from sqlalchemy import Column, BigInteger, ForeignKey, String
from backend.database import Base

class Caregiver(Base):
    __tablename__ = "CAREGIVER"

    userid = Column("userid", BigInteger, ForeignKey("USER.userid", ondelete="CASCADE"), primary_key=True)

class CaregiverPatient(Base):
    __tablename__ = "CAREGIVER_PATIENT"

    caregiver_id = Column("caregiverid", BigInteger, ForeignKey("CAREGIVER.userid", ondelete="CASCADE"), primary_key=True)
    patient_id = Column("patientid", BigInteger, ForeignKey("PATIENT.userid", ondelete="CASCADE"), primary_key=True)
    relationship_to_patient = Column("relationshiptopatient", String(100), nullable=False)
