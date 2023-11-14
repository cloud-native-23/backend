from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase

from app.models.stadium import Stadium
from app.models.user import User
from app.schemas.stadium import (
    StadiumCreate,
    StadiumUpdate,
    StadiumList
)


class CRUDStadium(CRUDBase[Stadium, StadiumCreate, StadiumUpdate]):
    # TODO: separate each function or one function with dynamic filter?
    def get_by_stadium_id(
        self, db: Session, *, stadium_id: int
    ) -> Optional[Stadium]:
        return (
            db.query(Stadium).filter(Stadium.id == stadium_id).first()
        )
    
    def get_stadium_list(
            self, 
            db: Session, 
            *, 
            user_id: int,
            is_query_with_created_user: bool = True
    ) -> Optional[List[StadiumList]]:
        selected_columns = (Stadium.id ,Stadium.name, Stadium.picture, Stadium.area)
        # return all stadium
        stadiums_query = db.query(*selected_columns)
        #filter by created user
        if is_query_with_created_user:
            stadiums_query = stadiums_query.filter(Stadium.created_user == user_id)

        stadiums = stadiums_query.all()
        
        return stadiums
    
    # TODO: wait for user validation
    # def create(self, db: Session, *, obj_in: StadiumCreate, current_user: User) -> Stadium:
    def create(self, db: Session, *, obj_in: StadiumCreate) -> Stadium:

        #TBC get_by_user_uuid name?
        # user_in = crud.user.get_by_user_uuid(
        #     db=db, room_id=obj_in.created_user.id
        # )
        db_obj = Stadium(
            name=obj_in.name,
            address=obj_in.address,
            picture=obj_in.picture,
            area=obj_in.area,
            description=obj_in.description,
            # created_user = user_in.id
            created_user = obj_in.created_user
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, db_obj: Stadium):
        db.delete(db_obj)
        db.commit()
        return True
    
    def update(
        self, db: Session, *, db_obj: Stadium, obj_in: Union[StadiumUpdate, Dict[str, Any]]
    ) -> Stadium:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
stadium = CRUDStadium(Stadium)