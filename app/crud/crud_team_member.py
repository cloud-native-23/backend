from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.team_member import TeamMember
from app.models.team import Team
from app.models.user import User
from app.models.order import Order
from app.schemas.team_member import TeamMemberCreate, TeamMemberUpdate

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
        rows_affected = (
            db.query(TeamMember)
            .filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
            .update({"status": 0})
        )

        # Commit the changes to the database
        db.commit()

        # Check if the update was successful (at least one row affected)
        if rows_affected > 0:
            return True
        else:
            return False
        
    def get_all_team_member_email_by_team_id(self, db=Session, *, team_id:int):
        # team_members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
        # team_member_emails = [db.query(User.email).filter(User.id == member.user_id).scalar() for member in team_members]
        # renters = (
        #     db.query(User.email)
        #     .filter(User.id == Team.renter_id)
        #     .join(Team, Team.id == team_id)
        #     .all()
        # )


        # return team_member_emails
    

        team_members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

        # Collect email addresses of team members
        team_member_emails = [db.query(User.email).filter(User.id == member.user_id).scalar() for member in team_members]

        order = (
            db.query(Order)
            .join(Team, Order.id == Team.order_id)
            .filter(Team.id == team_id)
            .first()
        )
        if order and order.renter_id:
            renter = (
                db.query(User)
                .filter(User.id == order.renter_id)
                .first()
            )
        all_emails = [renter.email] + team_member_emails
        return all_emails

team_member = CRUDTeamMember(TeamMember)
