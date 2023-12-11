import json
from typing import Any, Optional
from datetime import timedelta, datetime

import requests
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
#from loguru import logger
from sqlalchemy.orm import Session,joinedload

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.routers import deps
import traceback
from app.email.send_email import send_email_background


router = APIRouter()


@router.post("/my-rent-list/", response_model=schemas.OrderRentResponse)
def get_rent_list(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    rent_list = crud.order.get_user_order_history(db=db, user_id=current_user.id)

    
    return {"orders": rent_list}

@router.post("/order-cancel", response_model=schemas.OrderCancelResponse)
def cancel_order(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    order_id: int = None
):
    
    if crud.order.check_order_status(db=db, order_id=order_id):
        cancel_result = crud.order.cancel_order_by_id(db=db, order_id=order_id)
        team_member_emails = crud.order.get_order_member_email(db=db, order_id=order_id)
        order_info = crud.order.get_by_order_id(db=db, order_id=order_id)
        stadium_info = crud.stadium.get_by_stadium_court_id(db=db, stadium_court_id=order_info.stadium_court_id)
        stadium_court_info = crud.stadium_court.get_by_stadium_court_id(db=db, stadium_court_id=order_info.stadium_court_id)
        for email in team_member_emails:
            send_email_background(
                background_tasks,
                '訂單取消通知',
                '您的訂單已被取消！<br><br>'
                '訂單資訊：<br>'
                '日期: ' + str(order_info.date) + '<br>'
                '時間: ' + str(order_info.start_time) + ':00-' + str(order_info.start_time + 1) + ':00<br>'
                '地點: ' + stadium_info.name + ' ' + stadium_info.venue_name + ' ' + stadium_court_info.name ,
                [str(email)]
            )

    else:
        raise HTTPException(status_code=400, detail="Order is not available to cancel.")
    

    return {"message": "success", "order": cancel_result.__dict__}