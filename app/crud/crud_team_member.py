from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.team_member import TeamMember
from app.schemas.team_member import TeamMemberCreate, TeamMemberUpdate
from app.models.team import Team

class CRUDTeamMember(CRUDBase[TeamMember, TeamMemberCreate, TeamMemberUpdate]):
    def get_by_team_member_id(self, db: Session, *, team_member_id: int) -> Optional[TeamMember]:
        return db.query(TeamMember).filter(TeamMember.team_member_id == team_member_id).first()
    
    def get_all_by_team_id(self, db: Session, *, team_id: int) -> Optional[TeamMember]:
        return db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    
    def get_all_by_user_id(self, db: Session, *, user_id: int) -> Optional[TeamMember]:
        return db.query(TeamMember).filter(TeamMember.user_id == user_id).all()

    def create(self, db: Session, *, obj_in: TeamMemberCreate) -> TeamMember:
        db_obj = TeamMember(
            team_member_id = obj_in.team_member_id,
            team_id = obj_in.team_id,
            user_id = obj_in.user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: TeamMember, obj_in: Union[TeamMemberUpdate, Dict[str, Any]]
    ) -> TeamMember:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def delete_by_team_member_id(self, db: Session, *, team_member_id: str):
        if team_member_id is not None or team_member_id != "":
            db_objs = self.get_by_team_member_id(team_member_id)
            for db_obj in db_objs:
                db.delete(db_obj)
            db.commit()
        return True
    
    def leave_team(self, db=Session, *, team_id:int, user_id: int):
        db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id).update({"status": 0})
        db.commit()
        return True

team_member = CRUDTeamMember(TeamMember)
