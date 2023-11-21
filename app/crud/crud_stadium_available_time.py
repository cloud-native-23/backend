from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase

from app.models.stadium_available_time import StadiumAvailableTime
from app.schemas.stadium_available_time import (
    StadiumAvailableTimeCreate,
    StadiumAvailableTimeUpdate
)


class CRUDStadiumAvailableTime (CRUDBase[StadiumAvailableTime, StadiumAvailableTimeCreate, StadiumAvailableTimeUpdate]):
    
    def get_all_by_stadium_id(
        self, db: Session, *, stadium_id: int
    ) -> Optional[StadiumAvailableTime]:
        return (
            db.query(StadiumAvailableTime).filter(StadiumAvailableTime.stadium_id == stadium_id).all()
        )

    
    def create(self, db: Session, *, obj_in: StadiumAvailableTimeCreate, weekday: int, stadium_id: int) -> StadiumAvailableTime:
        db_obj = StadiumAvailableTime(
            stadium_id=stadium_id,
            weekday=weekday,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    
    def delete_by_stadium_court_id(self, db: Session, *, stadium_id: str):
        #in update stadium page, if update stadium_court, call this 
        if stadium_id is not None or stadium_id != "":
            db_objs = self.get_all_by_stadium_id(stadium_id)
            for db_obj in db_objs:
                db.delete(db_obj)
            db.commit()
        return True
    
    def get_available_times(
        self, db: Session, *,stadium_id: int
    ):
        """
        Get available time slots for a stadium on a given weekday.
        """
        available_times = (
            db.query(StadiumAvailableTime.start_time, StadiumAvailableTime.end_time)
            .filter(
                StadiumAvailableTime.stadium_id == stadium_id
            )
            .first()
        )
        return available_times
    
stadium_available_time = CRUDStadiumAvailableTime(StadiumAvailableTime)