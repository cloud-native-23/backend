from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase

from app.models.stadium_court import StadiumCourt
from app.schemas.stadium_court import (
    StadiumCourtCreate,
    StadiumCourtUpdate
)


class CRUDStadiumCourt(CRUDBase[StadiumCourt, StadiumCourtCreate, StadiumCourtUpdate]):
    # TODO: separate each function or one function with dynamic filter?
    def get_by_stadium_court_id(
        self, db: Session, *, stadium_court_id: int
    ) -> Optional[StadiumCourt]:
        return (
            db.query(StadiumCourt).filter(StadiumCourt.id == stadium_court_id).first()
        )
    
    def get_all_by_stadium_id(
        self, db: Session, *, stadium_id: int
    ) -> Optional[StadiumCourt]:
        return (
            db.query(StadiumCourt).filter(StadiumCourt.stadium_id == stadium_id).all()
        )

    
    def create(self, db: Session, *, obj_in: StadiumCourtCreate, stadium_id: int) -> StadiumCourt:
        db_obj = StadiumCourt(
            stadium_id=stadium_id,
            name=obj_in.name,
            max_number_of_people=obj_in.max_number_of_people
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_by_stadium_id(self, db: Session, *, stadium_id: str):
        if stadium_id is not None or stadium_id != "":
            db_objs = self.get_all_by_stadium_id(stadium_id)
            for db_obj in db_objs:
                db.delete(db_obj)
            db.commit()
        return True
    
    def delete_by_stadium_court_id(self, db: Session, *, stadium_court_id: str):
        #in update stadium page, if update stadium_court, call this 
        if stadium_court_id is not None or stadium_court_id != "":
            db_objs = self.get_by_stadium_court_id(stadium_court_id)
            for db_obj in db_objs:
                db.delete(db_obj)
            db.commit()
        return True
    
    

    
stadium_court = CRUDStadiumCourt(StadiumCourt)