from sqlalchemy import Column, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from app.database.base_class import Base


class StadiumCourtDisable(Base):
    __tablename__ = "StadiumCourtDisable"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stadium_court_id = Column(
        Integer,
        ForeignKey("StadiumCourt.id", ondelete="CASCADE"),
        nullable=False
    )
    datetime = Column(DateTime(timezone=True))
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)