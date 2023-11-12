from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from app import crud
from app.crud.base import CRUDBase

from app.models.stadium_disable import StadiumDisable
from app.schemas.stadium_disable import (
    StadiumDisableCreate,
    StadiumDisableUpdate
)


class CRUDStadiumDisable(CRUDBase[StadiumDisable, StadiumDisableCreate, StadiumDisableUpdate]):
    
    def get_all_by_stadium_id(
        self, db: Session, *, stadium_id: int
    ) -> Optional[StadiumDisable]:
        return (
            db.query(StadiumDisable).filter(StadiumDisable.id == stadium_id).all()
        )

    
    def create(self, db: Session, *, obj_in: StadiumDisableCreate) -> StadiumDisable:
        db_obj = StadiumDisable(
            stadium_id=obj_in.stadium_id,
            datetime=obj_in.datetime,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    
    def delete_by_stadium_id(self, db: Session, *, stadium_id: str):
        #in update stadium page, if update stadium_court, call this 
        if stadium_id is not None or stadium_id != "":
            db_objs = self.get_all_by_stadium_id(stadium_id)
            for db_obj in db_objs:
                db.delete(db_obj)
            db.commit()
        return True
    
    def is_disabled(
        self, db: Session, *, stadium_id: int, date: datetime, start_time: int, end_time: int
    ) -> bool:
        """
        Check if the stadium is disabled at a specific time.
        """
        return (
            db.query(StadiumDisable)
            .filter(
                StadiumDisable.stadium_id == stadium_id,
                StadiumDisable.date == date,
                StadiumDisable.start_time <= end_time,
                StadiumDisable.end_time >= start_time,
            )
            .first() is not None
        )
    
stadium_disable = CRUDStadiumDisable(StadiumDisable)