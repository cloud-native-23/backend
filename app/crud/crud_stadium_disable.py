from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase

from app.models.stadium_disable import StadiumDisable
from app.schemas.stadium_disable import (
    StadiumDisableCreate,
    StadiumDisableUpdate
)


class CRUDStadiumDisable(CRUDBase[StadiumDisable, StadiumDisableCreate, StadiumDisableUpdate]):
    
    def get_all_by_stadium_court_id(
        self, db: Session, *, stadium_court_id: int
    ) -> Optional[StadiumDisable]:
        return (
            db.query(StadiumDisable).filter(StadiumDisable.id == stadium_court_id).all()
        )

    
    def create(self, db: Session, *, obj_in: StadiumDisableCreate) -> StadiumDisable:
        db_obj = StadiumDisable(
            stadium_court_id=obj_in.stadium_court_id,
            datetime=obj_in.datetime,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    
    def delete_by_stadium_court_id(self, db: Session, *, stadium_court_id: str):
        #in update stadium page, if update stadium_court, call this 
        if stadium_court_id is not None or stadium_court_id != "":
            db_objs = self.get_all_by_stadium_court_id(stadium_court_id)
            for db_obj in db_objs:
                db.delete(db_obj)
            db.commit()
        return True
    
stadium_disable = StadiumDisable()