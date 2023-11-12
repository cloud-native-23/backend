from sqlalchemy import Column, Date, Integer, ForeignKey
from sqlalchemy.sql import func
from app.database.base_class import Base


class StadiumDisable(Base):
    __tablename__ = "StadiumDisable"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stadium_id = Column(
        Integer,
        ForeignKey("Stadium.id", ondelete="CASCADE"),
        nullable=False
    )
    date = Column(Date, nullable=False)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)