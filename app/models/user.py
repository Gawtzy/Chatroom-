from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)