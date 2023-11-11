from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.order import Order
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


user = CRUDOrder(Order)
