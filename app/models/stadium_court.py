from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
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
    is_enabled = Column(Boolean, nullable=False, default=True)