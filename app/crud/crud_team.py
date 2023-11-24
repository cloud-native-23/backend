from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    def get_by_team_id(self, db: Session, *, team_id: int) -> Optional[Team]:
        return db.query(Team).filter(Team.id == team_id).first()

    def get_by_order_id(self, db: Session, *, order_id: int) -> Optional[Team]:
        return db.query(Team).filter(Team.order_id == order_id).first()

    def create(self, db: Session, *, obj_in: TeamCreate) -> Team:
        db_obj = Team(
            order_id = obj_in.order_id,
            max_number_of_member = obj_in.max_number_of_member,
            orig_member_number = obj_in.orig_member_number,
            level_requirement = obj_in.level_requirement,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Team, obj_in: Union[TeamUpdate, Dict[str, Any]]
    ) -> Team:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def delete(self, db: Session, *, db_obj: Team):
        db.delete(db_obj)
        db.commit()
        return True


team = CRUDTeam(Team)
