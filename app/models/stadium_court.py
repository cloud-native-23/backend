from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.sql import func
from app.database.base_class import Base


class StadiumCourt(Base):
    __tablename__ = "StadiumCourt"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stadium_id = Column(
        Integer,
        ForeignKey("Stadium.id", ondelete="CASCADE"),
        nullable=False
    )
    name = Column(String, nullable=False)