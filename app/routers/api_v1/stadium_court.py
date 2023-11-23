import json
from typing import Any, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Response
#from loguru import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from app.routers import deps
from app.utils import get_weekday
from app.enums import LevelRequirement
from app.models.stadium_court import StadiumCourt
from app.models.order import Order
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.user import User


router = APIRouter()

@router.post("/rent-info", response_model=schemas.stadium_court.StadiumCourtWithRentInfoMessage)
def get_rent_info(
    stadium_id: int,
    date: str,
    start_time: int,
    # end_time: int,
    headcount: int,
    level_requirement: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve stadium_court with used status.
    """
    # 因為timetable已經考慮過available_time跟disable_time，故這裡輸入的input param一定是至少有一個場地可以滿足使用者需求的，直接考慮stadium_court跟order+team就好
    # 一個場地同一時段只會租給一組人，loop stadium_court找出是否已出租+租場地的人的資訊+隊伍資訊
    # get level_requirement_code
    level_requirement_candidates = []
    for enum in LevelRequirement:
        if enum.name.__contains__(level_requirement.upper()):
            level_requirement_candidates.append(enum.value)
    resultList = []
    # Step 1: Get stadium_courts by stadium_id
    stadium_courts = crud.stadium_court.get_all_by_stadium_id(db=db, stadium_id=stadium_id)
    # Step 2: Loop stadium_courts to find if court is already rented
    for stadium_court in stadium_courts:
        # query StadiumCourt, Order, Team
        query = db.query(StadiumCourt.id.label('stadium_court_id'), StadiumCourt.name.label('stadium_court_name'), User.name.label('renter_name'), Team.id.label('team_id'), Team.current_member_number, Team.max_number_of_member, Team.level_requirement) \
            .join(Order, StadiumCourt.id == Order.stadium_court_id) \
            .join(Team, Order.id == Team.order_id) \
            .join(User, Order.renter_id == User.id) \
            .filter(StadiumCourt.id == stadium_court.id) \
            .filter(Team.level_requirement.in_(level_requirement_candidates)).filter(Order.date == date) \
            .filter(Order.start_time == start_time) \
            # .filter(Team.max_number_of_member-Team.current_member_number >= headcount)
        result = query.first()
        # stadium_court is rented for this time
        if result is not None:
            result = schemas.stadium_court.StadiumCourtWithRentInfo(
                stadium_court_id = stadium_court.id,
                name = stadium_court.name,
                renter_name = result.renter_name,
                team_id = result.team_id,
                current_member_number = result.current_member_number,
                max_number_of_member = result.max_number_of_member,
                level_requirement = LevelRequirement(result.level_requirement).name.split('_'), # convert level_requirement from code to string
                status = '加入' if result.max_number_of_member - result.current_member_number >= headcount else '已滿'
            )
            resultList.append(result)
        # stadium_court is not rented for this time
        else:
            # print('tempp >>> ', result[0].current_member_number)
            result = schemas.stadium_court.StadiumCourtWithRentInfo(
                stadium_court_id = stadium_court.id,
                name = stadium_court.name,
                status = '租借'
            )
            resultList.append(result)

    return {"message": "success", "data": resultList}