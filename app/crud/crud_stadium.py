from typing import Any, Dict, Optional, Union, List
from datetime import datetime, date
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from sqlalchemy import func

from app import crud
from app.crud.base import CRUDBase

from app.models.stadium_court import StadiumCourt
from app.models.team import Team
from app.models.order import Order
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
    
    # get current people in stadium
    def get_stadium_current_people_count(
        self,
        db: Session, *, 
        stadium_id: int, 
    ) -> Any:
        
    # Get the stadium_court_ids for the given stadium_id
        stadium_court_ids = (
            db.query(StadiumCourt.id)
            .filter(StadiumCourt.stadium_id == stadium_id)
            .all()
        )
        
        if not stadium_court_ids:
            return None

        # Extract the ids as a list
        stadium_court_ids = [court_id for (court_id,) in stadium_court_ids]
        number_of_courts = len(stadium_court_ids)

        # Get the current date and time
        current_datetime = datetime.now(tz=ZoneInfo("Asia/Taipei"))
        # test_date = date(2023, 11, 17)
        # test_hour = 10

        # Get the sum of current_member_number for the selected orders and teams
        current_people_count = (
            db.query(func.sum(Team.current_member_number))
            .join(Order, Team.order_id == Order.id)
            .filter(Order.stadium_court_id.in_(stadium_court_ids))
            .filter(Order.date == current_datetime.date())
            .filter(Order.start_time <= current_datetime.hour)
            .filter(Order.end_time > current_datetime.hour)
            # .filter(Order.date == test_date)
            # .filter(Order.start_time <= test_hour)
            # .filter(Order.end_time > test_hour)
            .filter(Order.status == 1)  # Assuming status 1 represents an active order
            .scalar() or 0  # If there are no records, return 0
        )


        return current_people_count, number_of_courts

    def get_stadium_list(
            self, 
            db: Session, 
            *, 
            user_id: int,
    ) -> Optional[List[StadiumList]]:
        selected_columns = (Stadium.id ,Stadium.name, Stadium.venue_name, Stadium.picture, Stadium.area, Stadium.max_number_of_people)
        # return all stadium
        stadiums_query = db.query(*selected_columns)
        #filter by created user
        if user_id:
            stadiums_query = stadiums_query.filter(Stadium.created_user == user_id)

        stadiums = stadiums_query.all()
            
        return stadiums
    
    # TODO: wait for user validation
    # def create(self, db: Session, *, obj_in: StadiumCreate, current_user: User) -> Stadium:
    def create(self, db: Session, *, obj_in: StadiumCreate, user_id: int,) -> Stadium:

        #TBC get_by_user_uuid name?
        # user_in = crud.user.get_by_user_id(
        #     db=db, room_id=obj_in.created_user.id
        # )
        db_obj = Stadium(
            name=obj_in.name,
            address=obj_in.address,
            picture=obj_in.picture,
            area=obj_in.area,
            description=obj_in.description,
            created_user = user_id,
            venue_name = obj_in.venue_name,
            max_number_of_people = obj_in.max_number_of_people,
            # created_user = obj_in.created_user
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