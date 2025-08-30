from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base
class Room(Base):
    __tablename__ = "Room"
    name = Column(String(50), primary_key=True)
    password_hash = Column(String(255), nullable=False)
