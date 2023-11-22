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
        for session in obj_in.sessions:
            db_obj = StadiumDisable(
                stadium_id=obj_in.stadium_id,
                date=session.date,
                start_time=session.start_time,
                end_time=session.start_time+1,
            )
            db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    
    def delete_by_stadium_id_and_session(self, db: Session, *, stadium_id: int, date: date, start_time: int) -> bool:
        #in update stadium page, if update stadium_court, call this 
        stadium_disable = db.query(StadiumDisable).filter_by(stadium_id=stadium_id, date=date, 
                                                                start_time=start_time).first()
        if stadium_disable is not None:
            db.delete(stadium_disable)
            db.commit()
            return True
        else:
            return False
    
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
    
stadium_disable = CRUDStadiumDisable(StadiumDisable)