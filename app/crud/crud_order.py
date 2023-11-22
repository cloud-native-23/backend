from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta, datetime

from app.crud.base import CRUDBase
from app.models.order import Order
from app.models.team import Team
from app.models.stadium_court import StadiumCourt
from app.schemas.order import OrderCreate, OrderUpdate

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def get_by_order_id(self, db: Session, *, order_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.order_id == order_id).first()
    
    def get_all_by_renter_id(self, db: Session, *, renter_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.renter_id == renter_id).all()
    
    def get_all_by_stadium_court_id(self, db: Session, *, stadium_court_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.stadium_court_id == stadium_court_id).all()

    def create(self, db: Session, *, obj_in: OrderCreate) -> Order:
        db_obj = Order(
            stadium_court_id = obj_in.stadium_court_id,
            renter_id = obj_in.renter_id,
            datetime = obj_in.datetime,
            start_time = obj_in.start_time,
            end_time = obj_in.end_time,
            status = obj_in.status,
            is_matching = obj_in.is_matching,
            created_time = obj_in.created_time
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Order, obj_in: Union[OrderUpdate, Dict[str, Any]]
    ) -> Order:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def is_booked(
        self, db: Session, *,  stadium_id: int, date: datetime, start_time: int, end_time: int
    ):
        """
        Check if the court is booked at a specific time.
        """
        court_ids_subquery = (
            db.query(StadiumCourt.id)
            .filter(StadiumCourt.stadium_id == stadium_id)
            .all()
        )
        
        court_ids = [court_id for (court_id,) in court_ids_subquery]
        booked_court_count = (
            db.query(func.count(Order.stadium_court_id))
            .filter(
                Order.stadium_court_id.in_(court_ids),
                Order.date == date,
                Order.start_time == start_time,
                Order.end_time == end_time,
                Order.status == 1,
            )
            .scalar()
        )
        if booked_court_count !=0:
            return('at_least_one_court_be_booked')
        elif booked_court_count == len(court_ids):
            return('all_court_be_booked')
        else:
            return('none_be_booked')
    
    def headcount_and_level_requirement_checking(
        self, db: Session, *,  stadium_id: int, current_date: datetime, start_time: int, headcount:int, level_requirement:int
    ):
        court_ids_subquery = (
            db.query(StadiumCourt.id)
            .filter(StadiumCourt.stadium_id == stadium_id)
            .all()
        )
        court_ids = [court_id for (court_id,) in court_ids_subquery]
        for court_id in court_ids:
        # Check if there is an order for the court within the specified time range
            order = (
                db.query(Order)
                .filter(
                    Order.stadium_court_id == court_id,
                    Order.date == current_date,
                    Order.start_time == start_time,
                )
                .first()
            )
            if order:
                if order.is_matching == True:
                    #has order and is_matching,  checking limit about headcount and level
                    team = db.query(Team).filter(Team.order_id == order.id, Team.level_requirement<= level_requirement).first()
                    if (team.max_number_of_member - team.current_member_number) >= headcount:
                        return True
                    else:
                        return False
                elif order.is_matching == False:
                    #order is not for matching
                    return False
            else:
                #no order, can join
                return True


order = CRUDOrder(Order)
