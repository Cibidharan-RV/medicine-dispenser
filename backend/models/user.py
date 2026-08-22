from sqlalchemy import Column, BigInteger, String
from backend.database import Base

class User(Base):
    __tablename__ = "USER"

    userid = Column("userid", BigInteger, primary_key=True, index=True)
    username = Column("username", String(100), unique=True, nullable=False)
    hashed_password = Column("passwordhash", String(255), nullable=False)
    role = Column("role", String(20), nullable=False)
    first_name = Column("firstname", String(50), nullable=False)
    middle_name = Column("middlename", String(50))
    last_name = Column("lastname", String(50), nullable=False)
    phone_number = Column("phonenumber", String(15))
