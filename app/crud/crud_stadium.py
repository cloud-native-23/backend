from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase

from app.models.stadium import Stadium
from app.schemas.stadium import (
    StadiumCreate,
    StadiumUpdate
)


class CRUDStadium(CRUDBase[Stadium, StadiumCreate, StadiumUpdate]):
    # TODO: separate each function or one function with dynamic filter?
    def get_by_stadium_id(
        self, db: Session, *, stadium_id: int
    ) -> Optional[Stadium]:
        return (
            db.query(Stadium).filter(Stadium.id == stadium_id).first()
        )
    

    def create(self, db: Session, *, obj_in: StadiumCourtCreate) -> Stadium:

        #TBC get_by_user_uuid name?
        user_in = crud.user.get_by_user_uuid(
            db=db, room_id=obj_in.created_user.id
        )
        db_obj = Stadium(
            name=obj_in.name,
            address=obj_in.address,
            picture=obj_in.picture,
            area=obj_in.area,
            description=obj_in.description,
            created_user = user_in.id
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