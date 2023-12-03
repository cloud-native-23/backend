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
    level_requirement: int,
    db: Session = Depends(deps.get_db),
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve stadium_court with used status.
    """
    # 因為timetable已經考慮過available_time跟disable_time，故這裡輸入的input param一定是至少有一個場地可以滿足使用者需求的，直接考慮stadium_court跟order+team就好
    # 一個場地同一時段只會租給一組人，loop stadium_court找出是否已出租+租場地的人的資訊+隊伍資訊
    # 需考慮headcount
    # NEW ADD: 考慮headcount是否大於stadium max_number_of_people
    db_stadium = crud.stadium.get_by_stadium_id(db=db, stadium_id=stadium_id)
    if db_stadium is None:
        raise HTTPException(
            status_code=400,
            detail="Fail to find stadium with stadium_id = {}.".format(stadium_id),
        )
    resultList = []
    # Step 1: Get stadium_courts by stadium_id
    stadium_courts = crud.stadium_court.get_all_by_stadium_id(db=db, stadium_id=stadium_id)
    # Step 2: Loop stadium_courts to find if court is already rented
    for stadium_court in stadium_courts:
        # query StadiumCourt, Order, Team
        query = db.query(StadiumCourt.id.label('stadium_court_id'), StadiumCourt.name.label('stadium_court_name'), User.name.label('renter_name'), Team.id.label('team_id'), Team.current_member_number, Team.max_number_of_member, Team.level_requirement, Order.is_matching) \
            .join(Order, StadiumCourt.id == Order.stadium_court_id) \
            .join(Team, Order.id == Team.order_id) \
            .join(User, Order.renter_id == User.id) \
            .filter(StadiumCourt.is_enabled == True) \
            .filter(StadiumCourt.id == stadium_court.id) \
            .filter(Order.start_time == start_time) \
            .filter(Order.date == date) \
            # .filter(Order.is_matching == True)
            # .filter(Team.level_requirement <= level_requirement)
            # .filter(Team.max_number_of_member-Team.current_member_number >= headcount)
        result = query.first()
        # stadium_court is rented for this time
        if result is not None:
            orig_level_requirement_val = result.level_requirement
            result = schemas.stadium_court.StadiumCourtWithRentInfo(
                stadium_court_id = stadium_court.id,
                name = stadium_court.name,
                # is_matching = result.is_matching,
                renter_name = result.renter_name,
                team_id = result.team_id,
                current_member_number = result.current_member_number,
                max_number_of_member = result.max_number_of_member,
                level_requirement = LevelRequirement(result.level_requirement).value.split('_'), # convert level_requirement from code to string
                status = '', # '加入' if result.max_number_of_member - result.current_member_number >= headcount else ('已滿' if result.max_number_of_member == result.current_member_number else '無法加入')
                status_description = ''
            )
            # status check
            # if not enough place or level_requirement is not match => 無法加入; if current_member_number == max_number_of_member => 已滿; other => 加入
            if result.max_number_of_member == result.current_member_number: # is_match = False的也會在這邊 (create Team的時候max_number_of_member會等於current_member_number)
                result.status = '已滿'
            else:
                if orig_level_requirement_val <= level_requirement:
                    if result.max_number_of_member - result.current_member_number >= headcount:
                        result.status = '加入'
                    elif result.max_number_of_member - result.current_member_number < headcount:
                        result.status = '無法加入'
                        result.status_description = '欲加入人數大於隊伍剩餘可加入人數'
                # level_requirement is not match
                else:
                    result.status = '無法加入'
                    result.status_description = '能力程度不符'
            resultList.append(result)
        # stadium_court is not rented for this time
        else:
            result = schemas.stadium_court.StadiumCourtWithRentInfo(
                stadium_court_id = stadium_court.id,
                name = stadium_court.name,
                status = '租借',
                status_description = ''
            )
            if headcount > db_stadium.max_number_of_people: # 欲加入人數 > stadium_court最大人數
                result.status = '無法加入'
                result.status_description = '欲加入人數大於場地最大人數'
            resultList.append(result)

    return {"message": "success", "data": resultList}

@router.post("/rent", response_model=schemas.order.OrderWithTeamInfoMessage)
def rent(
    rent_obj_in: schemas.order.OrderCreateWithTeamInfo,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Rent stadium_court for specific date and time. (Includes creating Order, Team, TeamMember)
    """
    stadium_court = crud.stadium_court.get_by_stadium_court_id(db=db, stadium_court_id=rent_obj_in.stadium_court_id)
    if stadium_court is None or stadium_court.is_enabled == False:
        raise HTTPException(
            status_code=400,
            detail="Fail to rent stadium_court. No stadium_court data with stadium_court_id = {} or stadium_court is already disabled.".format(rent_obj_in.stadium_court_id),
        )
    try: 
         # create order
        create_order_obj = models.order.Order(
            stadium_court_id = rent_obj_in.stadium_court_id,
            renter_id = current_user.id,
            date = rent_obj_in.date,
            start_time = rent_obj_in.start_time,
            end_time = rent_obj_in.end_time,
            status = 1 if rent_obj_in else 0,
            is_matching = rent_obj_in.is_matching
        )
        db.add(create_order_obj)
        db.flush() # flush to get autoincremented id
        # create team
        create_team_obj = models.team.Team(
            order_id = create_order_obj.id,
            max_number_of_member = rent_obj_in.max_number_of_member,
            current_member_number = rent_obj_in.current_member_number,
            level_requirement = rent_obj_in.level_requirement
        )
        db.add(create_team_obj)
        db.flush() # flush to get autoincremented id
        # create team_member
        member_list = []
        for member_email in rent_obj_in.team_member_emails:
            member = db.query(User).filter(User.email == member_email).first()
            member_list.append(member)
            if member is None:
                raise HTTPException(
                    status_code=400,
                    detail="Fail to rent. No user data with email = {}.".format(member_email),
                )
            create_team_member_obj = models.team_member.TeamMember(
                team_id = create_team_obj.id,
                user_id = member.id,
                status = 1
            )
            db.add(create_team_member_obj)
        db.commit()

        team_members = [schemas.user.UserCredential(name=x.name, email=x.email) for x in member_list]
        data = schemas.order.OrderWithTeamInfo(
            id = create_order_obj.id,
            stadium_court_id = rent_obj_in.stadium_court_id,
            date = rent_obj_in.date,
            start_time = rent_obj_in.start_time,
            end_time = rent_obj_in.end_time, 
            current_member_number = rent_obj_in.current_member_number, 
            max_number_of_member = rent_obj_in.max_number_of_member, 
            is_matching = rent_obj_in.is_matching, 
            level_requirement = rent_obj_in.level_requirement, 
            team_id = create_team_obj.id,
            team_members = team_members
        )
        return {'message': 'success', 'data': data}
    except Exception as e:
        print('error >>> ', e)

        return {'message': 'fail. error: {}'.format(e)}

@router.post("/join", response_model=schemas.team.TeamInfoMessage)
def join(
    join_obj_in: schemas.team.TeamJoinInfo,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Join existing team.
    """
    team_obj = crud.team.get_by_team_id(db=db, team_id=join_obj_in.team_id)
    if team_obj is None:
        raise HTTPException(
            status_code=400,
            detail="Fail to join. No team data with team_id = {}.".format(join_obj_in.team_id),
        )
    try:
        # update current_member_number of team
        team_obj.current_member_number += len(join_obj_in.team_member_emails)+1 # other team_member + current_user
        db.add(team_obj)
        # add current_user & team_member into TABLE team_member
        # current user
        # check if team_member already have data but status = False (if so, just update the status to True)
        team_member_obj = db.query(TeamMember).filter(TeamMember.team_id == join_obj_in.team_id, TeamMember.user_id == current_user.id).first()
        if team_member_obj is not None:
            team_member_obj.status = 1
            db.add(team_member_obj)
        else:
            user_create_team_member_obj = models.team_member.TeamMember(
                team_id = join_obj_in.team_id,
                user_id = current_user.id,
                status = 1
            )
            db.add(user_create_team_member_obj)
        # other team_member
        for member_email in join_obj_in.team_member_emails:
            member = db.query(User).filter(User.email == member_email).first()
            if member is None:
                raise HTTPException(
                    status_code=400,
                    detail="Fail to join. No user data with email = {}.".format(member_email),
                )
            # check if team_member already have data but status = False (if so, just update the status to True)
            team_member_obj = db.query(TeamMember).filter(TeamMember.team_id == join_obj_in.team_id, TeamMember.user_id == member.id).first()
            if team_member_obj is not None:
                team_member_obj.status = 1
                db.add(team_member_obj)
            else:
                create_team_member_obj = models.team_member.TeamMember(
                    team_id = join_obj_in.team_id,
                    user_id = member.id,
                    status = 1
                )
                db.add(create_team_member_obj)
        db.commit()

        data = schemas.team.TeamInfo(
            id = team_obj.id,
            order_id = team_obj.order_id,
            max_number_of_member = team_obj.max_number_of_member,
            current_member_number = team_obj.current_member_number,
            level_requirement = team_obj.level_requirement,
        )

        return {'message': 'success', 'team': data}
    except Exception as e:
        print('error >>> ', e)

        return {'message': 'fail. error: {}'.format(e)}