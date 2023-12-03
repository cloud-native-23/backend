from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, join
from datetime import timedelta, datetime

from app.crud.base import CRUDBase
from app.models.order import Order
from app.models.team import Team
from app.models.stadium_court import StadiumCourt
from app.models.stadium import Stadium
from app.models.team_member import TeamMember
from app.models.user import User
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
            .filter(StadiumCourt.is_enabled == True)
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
        court_available_count = 0
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
                    if team:
                        if (team.max_number_of_member - team.current_member_number) >= headcount:
                            court_available_count = court_available_count+1
            else:
                court_available_count = court_available_count+1
        if court_available_count>0:
            return True
        else:
            return False
            
    def get_user_order_history(
            self, db: Session, *, user_id: int
    ):
        orders = (
            db.query(Order.id, Order.date, Order.start_time, Order.end_time, Stadium.name, Stadium.venue_name, StadiumCourt.name, 
                    Order.status, Team.current_member_number, Team.max_number_of_member
            )
            .join(StadiumCourt, Order.stadium_court_id == StadiumCourt.id)
            .join(Stadium, StadiumCourt.stadium_id == Stadium.id)
            .join(Team, Order.id == Team.order_id)
            .filter(Order.renter_id == user_id)
            .order_by(Order.date, Order.start_time)
            .all()
        )

        order_history = []
        for order in orders:
            team_members = (
                db.query(User.name, User.email)
                .join(TeamMember, User.id == TeamMember.user_id)
                .join(Team, TeamMember.team_id == Team.id)
                .filter(Team.order_id == order[0])
                .filter(TeamMember.status == 1)
                .filter(TeamMember.user_id != user_id)
                .all()
            )
            team_member_data = [{'name': name, 'email': email} for name, email in team_members]

            if order[7] == 1:
                status = "已核准"
            else:
                status = "已取消"

            # Create a dictionary for the order
            order_data = {
                "order_id": order[0],
                "order_time": order[1],  
                "start_time": order[2], 
                "end_time": order[3],
                "stadium_name": order[4],  
                "venue_name": order[5],
                "court_name": order[6],  
                "status": status, 
                "current_member_number": order[8], 
                "max_number_of_member": order[9], 
                "team_members": team_member_data, 
            }

            order_history.append(order_data)

        return order_history
    
    def check_order_status(
            self, db: Session, *, order_id: int
    ):
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.status == 1:
            return True
        else:
            return False
        
    def cancel_order(
            self, db: Session, *, order_id: int
    ):
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = 0
            db.commit()
            db.refresh(order)
            return order
        else:
            return None

order = CRUDOrder(Order)
