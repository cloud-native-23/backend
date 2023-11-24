import json
from typing import Any, Optional
from datetime import timedelta, datetime

import requests
from fastapi import APIRouter, Depends, HTTPException, Response
#from loguru import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.routers import deps
import traceback


router = APIRouter()

#input team id and get_current_user
#return 200
    
@router.post("/leave", response_model=schemas.stadium_disable.StadiumDisableResponse)
def leave(
    team_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    leave team
    """
    #step 1 check team and current_user is in db
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
    isLeaveSuccessfully = crud.team_member.leave_team(db=db, team_id=team.id, user_id=current_user.id)
    if isLeaveSuccessfully:
        return {'message': 'success', 'data': None}
    else:
        return {'message': 'fail', 'data': None}
