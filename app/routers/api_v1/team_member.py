import json
from typing import Any, Optional
from datetime import timedelta, datetime

import requests
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
#from loguru import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.routers import deps
from app.email.send_email import send_email_background
import traceback

router = APIRouter()
    
@router.post("/leave", response_model=schemas.team_member.TeamMemberLeave)
def leave(
    team_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    leave team
    """
    if (team_id == '' or team_id is None):
        raise HTTPException(
            status_code=400,
            detail="Fail to leave team. Missing parameter: team_id"
        )
    team = crud.team.get_by_team_id(
        db=db, team_id=team_id)
    if not team:
        raise HTTPException(
            status_code=400,
            detail="No team to leave.",
        )
    leave_successfully = crud.team_member.leave_team(db = db, team_id = team.id, user_id = current_user.id)
    decrease_current_member_number_successfully = crud.team.decrease_current_member_number(db = db, team_id = team.id)
    if leave_successfully and decrease_current_member_number_successfully:
        order_info = crud.order.get_by_order_id(db=db, order_id=team.order_id)
        stadium_info = crud.stadium.get_by_stadium_court_id(db=db, stadium_court_id=order_info.stadium_court_id)
        stadium_court_info = crud.stadium_court.get_by_stadium_court_id(db=db, stadium_court_id=order_info.stadium_court_id)
        emails = crud.team_member.get_all_team_member_email_by_team_id(db = db, team_id = team.id)
    
        for email in emails:
            send_email_background(
                background_tasks,
                '成員退出通知',
                '成員:'+str(current_user.name)+' 已退出團隊<br><br>'
                '團隊訂單資訊：<br>'
                '日期: ' + str(order_info.date) + '<br>'
                '時間: ' + str(order_info.start_time) + ':00-' + str(order_info.start_time + 1) + ':00<br>'
                '地點: ' + stadium_info.name + ' ' + stadium_info.venue_name + ' ' + stadium_court_info.name ,
                [str(email)]
                )

        return {'message': 'success', 'data': None}
    else:
        raise HTTPException(
            status_code=400,
            detail="No team to leave.",
        )
