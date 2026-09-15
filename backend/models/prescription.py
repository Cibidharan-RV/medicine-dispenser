from sqlalchemy import Column, BigInteger, Date, ForeignKey, CheckConstraint
from backend.database import Base

class Prescription(Base):
    __tablename__ = "prescription"
    __table_args__ = (
        CheckConstraint("enddate >= startdate", name="chk_prescription_dates"),
    )

    prescription_id = Column("prescriptionid", BigInteger, primary_key=True, index=True)
    patient_id = Column("patientid", BigInteger, ForeignKey("patient.userid"), nullable=False)
    doctor_id = Column("doctorid", BigInteger, ForeignKey("doctor.userid"), nullable=False)
    prescription_date = Column("prescriptiondate", Date, nullable=False)
    start_date = Column("startdate", Date, nullable=False)
    end_date = Column("enddate", Date, nullable=False)
