from sqlalchemy import Column, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from app.database.base_class import Base


class StadiumAvailableTime(Base):
    __tablename__ = "StadiumAvailableTime"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stadium_id = Column(
        Integer,
        ForeignKey("Stadium.id", ondelete="CASCADE"),
        nullable=False
    )
    weekday = Column(Integer, nullable=False)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)

    def to_dict(self):
        return {field.name:getattr(self, field.name) for field in self.__table__.c}