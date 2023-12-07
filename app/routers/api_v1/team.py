import json
from typing import Any, Optional
from datetime import timedelta, datetime

import requests
from fastapi import APIRouter, Depends, HTTPException, Response
#from loguru import logger
from sqlalchemy.orm import Session,joinedload

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.routers import deps
import traceback


router = APIRouter()


@router.post("/my-join-list/", response_model=schemas.TeamJointListResponse)
def get_join_list(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    print('current_user.id',current_user.id)
    join_query = (
        db.query(models.Team, models.Order, models.Stadium, models.StadiumCourt, models.User, models.TeamMember)
        .join(models.Order, models.Order.id == models.Team.order_id)
        .join(models.StadiumCourt, models.StadiumCourt.id == models.Order.stadium_court_id)
        .join(models.Stadium, models.Stadium.id == models.StadiumCourt.stadium_id)
        .join(models.User, models.User.id == models.Order.renter_id)
        .join(models.TeamMember, models.TeamMember.team_id == models.Team.id)
        .filter(models.TeamMember.user_id == current_user.id)
        .order_by(models.Order.date, models.Order.start_time)
    )

    # Execute the query and fetch the results
    results = join_query.all()

    # Transform the results into the desired response format
    team_joint_list = []
    for team, order, stadium, court, renter, team_member in results:
        if order.status == 1 and team_member.status == 1:
            join_status = "已加入"
        elif order.status == 0:
            join_status = "已取消"
        elif order.status == 1 and team_member.status == 0:
            join_status = "已退出"
        team_data = {
            "team_id": team.id,
            "order_time":order.date,
            "start_time": order.start_time,
            "end_time": order.end_time,
            "stadium_name": stadium.name,
            "venue_name": stadium.venue_name,
            "court_name": court.name,
            "current_member_number": team.current_member_number,
            "max_number_of_member": team.max_number_of_member,
            "renter_name": renter.name,
            "renter_email": renter.email,
            "join_status": join_status
        }

        # Fetch team members
        team_members = (
            db.query(models.User.name, models.User.email)
            .join(models.TeamMember, models.TeamMember.user_id == models.User.id)
            .filter(models.TeamMember.team_id == team.id)
            .filter(models.TeamMember.status==1)
            .filter(models.TeamMember.user_id!=current_user.id)
            .all()
        )

        team_data["team_members"] = [{"name": name, "email": email} for name, email in team_members]
        team_joint_list.append(team_data)

    return {"team_joint_list": team_joint_list}