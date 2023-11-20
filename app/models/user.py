from sqlalchemy import Boolean, Column, DateTime, String, Integer
from sqlalchemy.sql import func
from app.database.base_class import Base


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, default="--")
    password = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    picture = Column(String, nullable=True)
    is_provider = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)