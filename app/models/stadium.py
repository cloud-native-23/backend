from sqlalchemy import Column, DateTime, String, Integer, Float, ForeignKey
from sqlalchemy.sql import func
from app.database.base_class import Base


class Stadium(Base):
    __tablename__ = "Stadium"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    venue_name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    area = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    max_number_of_people = Column(Integer, nullable=False)
    created_user = Column(
        Integer,
        ForeignKey("User.id"),
        nullable=False)