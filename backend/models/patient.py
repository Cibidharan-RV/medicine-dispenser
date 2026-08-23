from sqlalchemy import Column, BigInteger, Date, String, ForeignKey
from backend.database import Base

class Patient(Base):
    __tablename__ = "patient"

    userid = Column("userid", BigInteger, ForeignKey("USER.userid", ondelete="CASCADE"), primary_key=True)
    date_of_birth = Column("dateofbirth", Date, nullable=False)
    gender = Column("gender", String(20))
    street = Column("street", String(150))
    city = Column("city", String(100))
    state = Column("state", String(100))
    postal_code = Column("postalcode", String(10))
