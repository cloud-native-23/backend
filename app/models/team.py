from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.sql import func
from app.database.base_class import Base


class Team(Base):
    __tablename__ = "Team"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(
        Integer,
        ForeignKey("Order.id", ondelete="CASCADE"),
        nullable=False
    )
    max_number_of_member = Column(Integer, nullable=False)
    current_member_number = Column(Integer, nullable=False)
    level_requirement = Column(Integer, nullable=False)