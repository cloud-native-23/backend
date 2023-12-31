from sqlalchemy import Boolean, Column, Date, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from app.database.base_class import Base


class Order(Base):
    __tablename__ = "Order"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stadium_court_id = Column(
        Integer,
        ForeignKey("StadiumCourt.id", ondelete="CASCADE"),
        nullable=False
    )
    renter_id = Column(
        Integer,
        ForeignKey("User.id", ondelete="CASCADE")
    )
    date = Column(Date, nullable=False)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    is_matching = Column(Boolean, nullable=False)
    created_time = Column(DateTime(timezone=True), default=func.now()) # aka. rent_time