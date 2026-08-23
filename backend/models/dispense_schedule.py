from sqlalchemy import Column, BigInteger, Integer, Date, Time, ForeignKey, CheckConstraint
from backend.database import Base

class DispenseSchedule(Base):
    __tablename__ = "dispense_schedule"
    __table_args__ = (
        CheckConstraint("quantitytodispense > 0", name="chk_schedule_quantity"),
        CheckConstraint("enddate >= startdate", name="chk_schedule_dates")
    )

    schedule_id = Column("scheduleid", BigInteger, primary_key=True, index=True)
    prescription_item_id = Column("prescriptionitemid", BigInteger, ForeignKey("PRESCRIPTION_ITEM.prescriptionitemid", ondelete="CASCADE"), nullable=False)
    scheduled_time = Column("scheduledtime", Time, nullable=False)
    quantity_to_dispense = Column("quantitytodispense", Integer, nullable=False)
    start_date = Column("startdate", Date, nullable=False)
    end_date = Column("enddate", Date, nullable=False)
