from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from datetime import timedelta, datetime, date

from app import crud
from app.crud.base import CRUDBase

from app.models.stadium_disable import StadiumDisable
from app.schemas.stadium_disable import (
    StadiumDisableCreate,
    StadiumDisableUpdate,
    StadiumDisableInDBBase
)


class CRUDStadiumDisable(CRUDBase[StadiumDisable, StadiumDisableCreate, StadiumDisableUpdate]):
    
    def get_all_by_stadium_id(
        self, db: Session, *, stadium_id: int
    ) -> Optional[StadiumDisable]:
        return (
            db.query(StadiumDisable).filter(StadiumDisable.id == stadium_id).all()
        )
    
    def get_by_stadium_id_and_session(
         self, db: Session, *, obj_in: StadiumDisableInDBBase
    ) -> Optional[StadiumDisable]:
        return (
            db.query(StadiumDisable)
            .filter_by(StadiumDisable.stadium_id==obj_in.stadium_id, StadiumDisable.date==obj_in.date, 
                       StadiumDisable.start_time==obj_in.start_time, StadiumDisable.end_time==obj_in.end_time).first()
        )           

    
    def create(self, db: Session, *, obj_in: StadiumDisableCreate) -> StadiumDisable:
        
        db_obj = StadiumDisable(
            stadium_id=obj_in.stadium_id,
            date=obj_in.date,
            start_time=obj_in.start_time,
            end_time=obj_in.start_time+1,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    
    def delete_by_stadium_id_and_session(self, db: Session, *, stadium_id: int, date: date, start_time: int) -> StadiumDisable:
        #in update stadium page, if update stadium_court, call this 
        stadium_disable = db.query(StadiumDisable).filter_by(stadium_id=stadium_id, date=date, 
                                                                start_time=start_time).first()
        if stadium_disable is not None:
            db.delete(stadium_disable)
            db.commit()
            return stadium_disable
        else:
            return None
    
    def is_disabled(
        self, db: Session, *, stadium_id: int, date: date, start_time: int
    ) -> bool:
        """
        Check if the stadium is disabled at a specific time.
        """
        return (
            db.query(StadiumDisable)
            .filter(
                StadiumDisable.stadium_id == stadium_id,
                StadiumDisable.date == date,
                StadiumDisable.start_time == start_time,
            )
            .first() is not None
        )
    
    def generate_time_slots(self, start_date: date, start_time: int, end_date: date, end_time: int, stadium_open_hour: int, stadium_close_hour: int):
    

        current_datetime = datetime.combine(start_date, datetime.min.time()) + timedelta(hours=start_time)

        result = []
        while current_datetime < datetime.combine(end_date, datetime.min.time()) + timedelta(hours=end_time):
            current_date = current_datetime.date()
            current_hour = current_datetime.hour

            if stadium_open_hour <= current_hour < stadium_close_hour:
                result.append({'date': current_date, 'start_time': current_hour})

            current_datetime += timedelta(hours=1)

        return result
    
stadium_disable = CRUDStadiumDisable(StadiumDisable)