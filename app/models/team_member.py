from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.sql import func
from app.database.base_class import Base


class TeamMember(Base):
    __tablename__ = "TeamMember"
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(
        Integer,
        ForeignKey("Team.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id = Column(
        Integer,
        ForeignKey("User.id", ondelete="CASCADE"),
        nullable=False
    )
    status = Column(Integer, nullable=False)