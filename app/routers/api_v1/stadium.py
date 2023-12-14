import json
from typing import Any, Optional
from datetime import timedelta, datetime, date

import requests
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
#from loguru import logger
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.routers import deps
from app.enums import LevelRequirement
from app.email.send_email import send_email_background
from app.models.stadium import Stadium
from app.models.stadium_available_time import StadiumAvailableTime
from app.models.stadium_court import StadiumCourt
from app.models.order import Order
from app.models.team import Team
import traceback


router = APIRouter()


@router.post("/timetable/", response_model=schemas.StadiumAvailabilityResponse)
def get_stadium_availability(
    stadium_id: int,
    query_date: str,
    headcount: int,
    level_requirement: str,
    db: Session = Depends(deps.get_db)
):
    try:
        stadium = crud.stadium.get_by_stadium_id(db=db, stadium_id=stadium_id)
        if not stadium:
            raise HTTPException(status_code=404, detail="Stadium not found")

        # Convert query_date to datetime
        query_date = datetime.strptime(query_date, "%Y-%m-%d")

        # Initialize the response data structure
        response_data = {
            "stadium_id": stadium_id,
            "query_date": query_date,
            "message": "success",
            "data": [],
        }
        available_times = crud.stadium_available_time.get_available_times(
            db=db, stadium_id=stadium_id
        )

        # Iterate over the next 7 days
        for i in range(7):
            current_date = query_date + timedelta(days=i)
            availability_data = {"day_{}".format(i + 1): {}}
            # Iterate over the available time slots in a day
            for start_time in range(available_times.start_time, available_times.end_time):   
                end_time = start_time + 1

                #先看這個時段有沒有被disable
                # Check if the stadium is disabled at this time
                is_disabled = crud.stadium_disable.is_disabled(
                    db=db, stadium_id=stadium_id, date=current_date, start_time=start_time
                )

                if is_disabled:
                    availability_data["day_{}".format(i + 1)][str(start_time)] = "Disabled"
                else:
                    # Check if the court is booked at this time
                    # 看該時段之下，該stadium之下的所有stadium court是否被借走
                    # 如果至少還有一個可以被租借（沒有order紀錄）則 Available
                    booking_result = crud.order.is_booked(
                        db=db, stadium_id=stadium_id, date=current_date, start_time=start_time, end_time=end_time
                    )
                    levels = [level.values[1] for level in LevelRequirement if level_requirement.upper() in level.name]
                    headcount_and_level_checking_result = crud.order.headcount_and_level_requirement_checking(
                        db=db, stadium_id=stadium_id, current_date=current_date, start_time=start_time, headcount= headcount, levels = levels
                    )
                    if booking_result == 'all_court_be_booked':
                        availability_data["day_{}".format(i + 1)][str(start_time)] = "Booked"
                    elif booking_result == 'none_be_booked':
                        availability_data["day_{}".format(i + 1)][str(start_time)] = "Available"
                    elif booking_result == 'at_least_one_court_be_booked':
                        if headcount_and_level_checking_result==True:
                            availability_data["day_{}".format(i + 1)][str(start_time)] = "Available"
                        else:
                            availability_data["day_{}".format(i + 1)][str(start_time)] = "Booked"
            response_data["data"].append(availability_data)

        return response_data

    except Exception as e:
        print('Error:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/providertimetable/", response_model=schemas.StadiumAvailabilityResponse)
def get_stadium_availability_for_provider(
    stadium_id: int,
    query_date: str,
    db: Session = Depends(deps.get_db)
):
    #有訂單/可下架/已下架 下架單位是stadium
    #已下架->已經被disable
    #有訂單->該stadium 之下的所有 stadium court ，至少有一個stadium court有該時段的訂單
    try:
        stadium = crud.stadium.get_by_stadium_id(db=db, stadium_id=stadium_id)
        if not stadium:
            raise HTTPException(status_code=404, detail="Stadium not found")

        # Convert query_date to datetime
        query_date = datetime.strptime(query_date, "%Y-%m-%d")

        # Initialize the response data structure
        response_data = {
            "stadium_id": stadium_id,
            "query_date": query_date,
            "message": "success",
            "data": [],
        }
        available_times = crud.stadium_available_time.get_available_times(
            db=db, stadium_id=stadium_id
        )
        # Iterate over the next 7 days
        for i in range(7):
            current_date = query_date + timedelta(days=i)
            availability_data = {"day_{}".format(i + 1): {}}
            # Iterate over the available time slots in a day
            for start_time in range(available_times.start_time, available_times.end_time):  
                end_time = start_time + 1
                #先看這個時段有沒有被disable
                # Check if the stadium is disabled at this time
                is_disabled = crud.stadium_disable.is_disabled(
                    db=db, stadium_id=stadium_id, date=current_date, start_time=start_time
                )

                if is_disabled:
                    availability_data["day_{}".format(i + 1)][str(start_time)] = "disable"
                else:
                    # Check if the court is booked at this time
                    result = crud.order.is_booked(
                        db=db, stadium_id=stadium_id, date=current_date, start_time=start_time, end_time=end_time
                    )

                    if result=='at_least_one_court_be_booked':
                        availability_data["day_{}".format(i + 1)][str(start_time)] = "has_order"
                    else:
                        availability_data["day_{}".format(i + 1)][str(start_time)] = "no_order"
            response_data["data"].append(availability_data)

        return response_data

    except Exception as e:
        print('Error:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/create", response_model=schemas.stadium_court.StadiumCourtCreateWithMessage)
def create_stadium(
    *,
    db: Session = Depends(deps.get_db),
    stadium_court_in: schemas.StadiumCourtCreateList,
    # TODO: wait for user validation
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new stadium and stadium courts.
    """ 
    try:

        # Create Stadium
        stadium = crud.stadium.create(db=db, obj_in=stadium_court_in.stadium, user_id=current_user.id)

        # Create StadiumCourts
        stadium_courts = []
        for stadium_court_data in stadium_court_in.stadium_court_name:
            # Associate with the created stadium
            stadium_court = crud.stadium_court.create(db=db, name=stadium_court_data, stadium_id=stadium.id)
            stadium_courts.append({"stadium_court_id": stadium_court.id, "name": stadium_court.name})
        
        # Create StadiumAvailableTimes
        stadium_available_times = []
        for stadium_available_time_weekday in stadium_court_in.stadium_available_times.weekday:
            stadium_available_time = crud.stadium_available_time.create(db=db, obj_in=stadium_court_in.stadium_available_times, weekday=stadium_available_time_weekday,stadium_id=stadium.id)
            stadium_available_times.append(stadium_available_time.to_dict())

        # Adjust the response to include stadium, StadiumAvailableTimes and stadium courts
        return {"message": "success", "stadium": stadium, "stadium_available_times": [time for time in stadium_available_times], "stadium_court": [court for court in stadium_courts]}

    except Exception as e:
        print('Error:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stadium-list/", response_model=schemas.stadium.StadiumListMessage)
def get_stadium_list_with_created_user(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Retrieve stadium list w/ or w/o created_user.
    """
    try:
              
        stadiums = crud.stadium.get_stadium_list(db=db, user_id=None)

        stadiums_data = []
        for stadium_id, name, venue_name, picture, area,  max_number_of_people in stadiums:
            current_people_count, number_of_courts = crud.stadium.get_stadium_current_people_count(
            db=db, stadium_id=stadium_id
            )
            stadiums_data.append({'stadium_id': stadium_id, 'name': name, 'venue_name': venue_name, 'picture': picture, 'area': area, 
                                  'max_number_of_people': max_number_of_people*number_of_courts, 'current_people_count': current_people_count})
            
        return {"message": "success", "stadium": stadiums_data}
    
    except Exception as e:
        print('Error:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/info", response_model=schemas.stadium.StadiumInfoMessage)
def get_stadium(
    stadium_id: int,
    db: Session = Depends(deps.get_db),
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve stadium info with stadium_id.
    """
    stadium = crud.stadium.get_by_stadium_id(db=db, stadium_id=stadium_id)
    if stadium is None:
        raise HTTPException(
            status_code=400,
            detail="Fail to get stadium info. No stadium data with stadium_id = {}.".format(stadium_id),
        )
    stadium_courts = crud.stadium_court.get_all_by_stadium_id(db=db, stadium_id=stadium.id)
    stadium_available_times = crud.stadium_available_time.get_all_by_stadium_id(db=db, stadium_id=stadium_id)
    available_time_info = schemas.StadiumAvailableTimeForInfo(
        weekdays = [x.weekday for x in stadium_available_times],
        start_time = stadium_available_times[0].start_time if len(stadium_available_times) > 0 else None,
        end_time = stadium_available_times[0].end_time if len(stadium_available_times) > 0 else None
    )
    data = schemas.StadiumInfo(
        stadium_id = stadium.id,
        name = stadium.name,
        venue_name = stadium.venue_name,
        address = stadium.address,
        picture = stadium.picture,
        area = stadium.area,
        description = stadium.description,
        google_map_url = stadium.google_map_url,
        created_user = stadium.created_user,
        max_number_of_people = stadium.max_number_of_people,
        stadium_courts = [schemas.StadiumCourtForInfo(id=x.id, name=x.name) for x in stadium_courts],
        available_times = available_time_info
    )

    return {"message": "success", "data": data}

@router.delete("/delete", response_model=schemas.stadium.StadiumDeleteMessage)
def delete_stadium(
    stadium_id: int,
    db: Session = Depends(deps.get_db),
    # TODO: wait for user validation
    current_user: models.user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete stadium with stadium_id.
    """
    stadium = crud.stadium.get_by_stadium_id(db=db, stadium_id=stadium_id)
    if not stadium:
        raise HTTPException(
            status_code=400,
            detail="No stadium to delete.",
        )
    isDeleteSuccessfully = crud.stadium.delete(db=db, db_obj=stadium)
    if isDeleteSuccessfully:
        return {'message': 'success', 'data': None}
    else:
        return {'message': 'fail', 'data': None}

@router.post("/disable", response_model=schemas.stadium_disable.StadiumDisableResponse)
def disable_stadium(
    StadiumDisableContinue_in: schemas.stadium_disable.StadiumDisableContinue,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: models.user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Disable stadium with stadium_id.
    """
    stadium = crud.stadium.get_by_stadium_id(
        db=db, stadium_id=StadiumDisableContinue_in.stadium_id)
    if not stadium:
        raise HTTPException(
            status_code=400,
            detail="No stadium to disable.",
        )
    
    statium_available_times = crud.stadium_available_time.get_all_by_stadium_id(db=db, stadium_id=StadiumDisableContinue_in.stadium_id)

    disable_sessions = crud.stadium_disable.generate_time_slots(
        StadiumDisableContinue_in.start_date, StadiumDisableContinue_in.start_time, StadiumDisableContinue_in.end_date, 
        StadiumDisableContinue_in.end_time, statium_available_times[0].start_time, statium_available_times[0].end_time)
    
    if disable_sessions:
    
        return_data = []
        cancel_order_list = []      
        
        for session in disable_sessions:
            stadium_disable = crud.stadium_disable.is_disabled(
                db=db, stadium_id=StadiumDisableContinue_in.stadium_id, date=session['date'], start_time=session['start_time']
            )
            if stadium_disable:
                    continue

            disable_obj_in = schemas.stadium_disable.StadiumDisableCreate(
                stadium_id=StadiumDisableContinue_in.stadium_id,
                date=session['date'],
                start_time=session['start_time'],
                end_time=session['start_time']+1
            )
            
            disable_obj = crud.stadium_disable.create(db=db, obj_in=disable_obj_in)
            if disable_obj:
                return_data.append({'date': disable_obj.date, 'start_time': disable_obj.start_time})

                stadium_courts = crud.stadium_court.get_all_by_stadium_id(db=db, stadium_id=StadiumDisableContinue_in.stadium_id)
          
                for stadium_court in stadium_courts:
                    stadium_court_id = stadium_court.id
                    orders_to_be_cancelled = crud.order.get_all_id_by_date_and_start_time(
                        db=db, stadium_court_id=stadium_court_id ,date=disable_obj.date, start_time=disable_obj.start_time
                    )

                    if orders_to_be_cancelled:
                        for order_to_be_cancelled in orders_to_be_cancelled:
                            order_id = order_to_be_cancelled.id
                            cancel_order = crud.order.cancel_order_by_id(db=db, order_id=order_id)
                            cancel_order_list.append(cancel_order.id)
            else:
                return {'message': 'fail', 'stadium_id': StadiumDisableContinue_in.stadium_id, 'sessions': None, 'cancel_orders': None}
            
        stadium_info = crud.stadium.get_by_stadium_id(db=db, stadium_id=StadiumDisableContinue_in.stadium_id)
        for order in cancel_order_list:
            team_member_emails = crud.order.get_order_member_email(db=db, order_id=order)
            order_info = crud.order.get_by_order_id(db=db, order_id=order)
            stadium_court_info = crud.stadium_court.get_by_stadium_court_id(db=db, stadium_court_id=order_info.stadium_court_id)
            for email in team_member_emails:
                send_email_background(
                    background_tasks,
                    '訂單取消通知',
                    '因場館於該時段暫時關閉，<br>訂單已被取消！<br><br>'
                    '訂單資訊：<br>'
                    '日期: ' + str(order_info.date) + '<br>'
                    '時間: ' + str(order_info.start_time) + ':00-' + str(order_info.start_time + 1) + ':00<br>'
                    '地點: ' + stadium_info.name + ' ' + stadium_info.venue_name + ' ' + stadium_court_info.name ,
                    [str(email)]
                )

            
    else:
        raise HTTPException(
            status_code=400,
            detail="The disable time is not valid.",
        )
    
    if return_data:
        message = 'success'
    else:
        message = 'Stadium is already disabled at the time.'

    return {'message': message, 'stadium_id': StadiumDisableContinue_in.stadium_id,'sessions': return_data, 'cancel_orders': cancel_order_list}
    
@router.delete("/undisable", response_model=schemas.stadium_disable.StadiumUnDisableResponse)
def undisable_stadium(
    # StadiumUndisableContinue_in: schemas.stadium_disable.StadiumDisableContinue,
    stadium_id: int,
    start_date: date,
    start_time: int,
    end_date: date,
    end_time: int,
    db: Session = Depends(deps.get_db),
    current_user: models.user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Undisable stadium.
    """
    
    stadium = crud.stadium.get_by_stadium_id(
        db=db, stadium_id=stadium_id)
    if not stadium:
        raise HTTPException(
            status_code=400,
            detail="No stadium to undisable.",
        )
    
    statium_available_times = crud.stadium_available_time.get_all_by_stadium_id(db=db, stadium_id=stadium_id)

    undisable_sessions = crud.stadium_disable.generate_time_slots(
        start_date, start_time, end_date, 
        end_time, statium_available_times[0].start_time, statium_available_times[0].end_time)
    
    if undisable_sessions:  

        return_data = []

        for session in undisable_sessions:
            stadium_disable = crud.stadium_disable.is_disabled(
                db=db, stadium_id=stadium_id, date=session['date'], start_time=session['start_time']
            )
            if not stadium_disable:
                continue
            
            undisable_obj = crud.stadium_disable.delete_by_stadium_id_and_session(
                db=db, stadium_id=stadium_id, date=session['date'], start_time=session['start_time']
            )
            if undisable_obj:
                return_data.append({'date': undisable_obj.date, 'start_time': undisable_obj.start_time})
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Fail to undisable stadium. Stadium ID: {stadium_id}, Date: {session['date']}, Start Time: {session['start_time']}",
                )
            
    else:
        raise HTTPException(
            status_code=400,
            detail="The undisable time is not valid.",
        )
    if return_data:
            message = 'success'
    else:
        message = 'Stadium is not disabled at the time.'

    return {'message': message, 'stadium_id': stadium_id,'sessions': return_data}

@router.put("/", response_model=schemas.stadium.StadiumInfoMessage)
def update_stadium(
    background_tasks: BackgroundTasks,
    stadium_obj_in: schemas.stadium.StadiumUpdateAdditionalInfo,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update stadium info, including modifications to stadium_court and stadium_available_time.
    """
    orig_stadium = crud.stadium.get_by_stadium_id(db=db, stadium_id=stadium_obj_in.stadium_id)
    if orig_stadium is None:
        raise HTTPException(
            status_code=400,
            detail="Fail to update stadium. No stadium data with stadium_id = {}.".format(stadium_obj_in.stadium_id),
        )
    try:
        # save orig_max_number_of_people for later using
        orig_stadium_max_number_of_people = orig_stadium.max_number_of_people
        ### update stadium ###
        orig_stadium.name = stadium_obj_in.name
        orig_stadium.venue_name = stadium_obj_in.venue_name
        orig_stadium.address = stadium_obj_in.address
        orig_stadium.picture = stadium_obj_in.picture
        orig_stadium.area = stadium_obj_in.area
        orig_stadium.description = stadium_obj_in.description
        orig_stadium.google_map_url = stadium_obj_in.google_map_url
        orig_stadium.max_number_of_people = stadium_obj_in.max_number_of_people
        db.add(orig_stadium)
        ### update stadium_courts ###
        for stadium_court_in in stadium_obj_in.stadium_courts:
            if stadium_court_in.id is None:
                create_stadium_court = StadiumCourt(
                    stadium_id = orig_stadium.id,
                    name = stadium_court_in.name,
                    is_enabled = True
                )
                db.add(create_stadium_court)
            else:
                court = db.query(StadiumCourt) \
                    .filter(StadiumCourt.id == stadium_court_in.id, StadiumCourt.is_enabled == True).first()
                # if not in db => new add
                if court is None:
                    create_stadium_court = StadiumCourt(
                        stadium_id = orig_stadium.id,
                        name = stadium_court_in.name,
                        is_enabled = True
                    )
                    db.add(create_stadium_court)
                else: # update
                    court.name = stadium_court_in.name
                    db.add(court)
        # stadium_courts in db but not in api input => delete
        db_stadium_courts = db.query(StadiumCourt) \
            .filter(StadiumCourt.stadium_id == stadium_obj_in.stadium_id, StadiumCourt.is_enabled == True).all()
        stadium_courts_to_disable = [x for x in db_stadium_courts if x.id not in [y.id for y in stadium_obj_in.stadium_courts]]
        for disabled_court in stadium_courts_to_disable:
            disabled_court.is_enabled = False
            db.add(disabled_court)
            # update status of orders under this court to canceled
            orders = db.query(Order).filter(Order.stadium_court_id == disabled_court.id).all()
            for order in orders:
                order.status = 0
                db.add(order)

        # if updated max_number_of_people is smaller than before => cancel
        # check if existing team with max_number_of_member exceeding new max_number_of_people
        if orig_stadium_max_number_of_people is not None and orig_stadium_max_number_of_people > stadium_obj_in.max_number_of_people:
            orders_need_to_be_updated = db.query(Order) \
                    .join(StadiumCourt, Order.stadium_court_id == StadiumCourt.id) \
                    .join(Stadium, Stadium.id == StadiumCourt.stadium_id) \
                    .join(Team, Order.id == Team.order_id) \
                    .filter(Stadium.id == stadium_obj_in.stadium_id) \
                    .filter(Team.max_number_of_member > stadium_obj_in.max_number_of_people) \
                    .filter(StadiumCourt.is_enabled == True) \
                    .all()
            for exceeding_order in orders_need_to_be_updated:
                exceeding_order.status = 0
                db.add(exceeding_order)
        
        ### update stadium_available_times ###
        update_available_times = stadium_obj_in.available_times
        # delete all first
        db.query(StadiumAvailableTime).filter(StadiumAvailableTime.stadium_id == stadium_obj_in.stadium_id).delete()
        # create new available_times
        for weekday in update_available_times.weekdays:
            create_available_time = StadiumAvailableTime(
                stadium_id = orig_stadium.id,
                weekday = weekday,
                start_time = update_available_times.start_time,
                end_time = update_available_times.end_time
            )
            db.add(create_available_time)
        db.commit()    

        data = schemas.StadiumInfo(
            stadium_id = stadium_obj_in.stadium_id,
            name = stadium_obj_in.name,
            venue_name = stadium_obj_in.venue_name,
            address = stadium_obj_in.address,
            picture = stadium_obj_in.picture,
            area = stadium_obj_in.area,
            description = stadium_obj_in.description,
            google_map_url = stadium_obj_in.google_map_url,
            created_user = orig_stadium.created_user,
            max_number_of_people = stadium_obj_in.max_number_of_people,
            stadium_courts = [schemas.StadiumCourtForInfo(id=x.id, name=x.name) for x in crud.stadium_court.get_all_by_stadium_id(db=db, stadium_id=orig_stadium.id)],
            available_times = stadium_obj_in.available_times
        )

        # send mail => only send mail after successfully commit
        for disabled_court in stadium_courts_to_disable:
            canceled_orders_related_data = db.query(Order.date, Order.start_time, Order.end_time, StadiumCourt.name.label('stadium_court_name'), Stadium.name, Stadium.venue_name, Team.id.label('team_id')) \
                         .join(StadiumCourt, Order.stadium_court_id == StadiumCourt.id) \
                         .join(Stadium, StadiumCourt.stadium_id == Stadium.id) \
                         .join(Team, Order.id == Team.order_id) \
                         .filter(Order.stadium_court_id == disabled_court.id) \
                         .all()
            for order_related_data in canceled_orders_related_data:
                # get team member emails
                member_emails = crud.team_member.get_all_team_member_email_by_team_id(db=db, team_id=order_related_data.team_id)
                mail_content = '因租借場地已被下架，<br>訂單已被取消！<br><br>訂單資訊：<br>日期：{}<br>時間：{}<br>地點：{}<br>' \
                        .format(str(order_related_data.date), 
                                '{}:00-{}:00'.format(order_related_data.start_time, order_related_data.end_time), 
                                '{} {} {}'.format(order_related_data.name, order_related_data.venue_name, order_related_data.stadium_court_name))
                send_email_background(background_tasks, 'Stadium Matching - 訂單取消通知', mail_content, recipients=member_emails)

        # if updated max_number_of_people is smaller than before => cancel
        # check if existing team with max_number_of_member exceeding new max_number_of_people
        if orig_stadium_max_number_of_people is not None and orig_stadium_max_number_of_people > stadium_obj_in.max_number_of_people:
            canceled_orders_related_data = db.query(Order.date, Order.start_time, Order.end_time, StadiumCourt.name.label('stadium_court_name'), Stadium.name, Stadium.venue_name, Team.id.label('team_id')) \
                    .join(StadiumCourt, Order.stadium_court_id == StadiumCourt.id) \
                    .join(Stadium, Stadium.id == StadiumCourt.stadium_id) \
                    .join(Team, Order.id == Team.order_id) \
                    .filter(Stadium.id == stadium_obj_in.stadium_id) \
                    .filter(Team.max_number_of_member > stadium_obj_in.max_number_of_people) \
                    .filter(StadiumCourt.is_enabled == True) \
                    .all()
            for order_related_data in canceled_orders_related_data:
                # get team member emails
                member_emails = crud.team_member.get_all_team_member_email_by_team_id(db=db, team_id=order_related_data.team_id)
                mail_content = '因租借場地之最大使用人數調降，<br>隊伍人數超過場地之最大使用人數，<br>訂單已被取消！<br><br>訂單資訊：<br>日期：{}<br>時間：{}<br>地點：{}<br>' \
                        .format(str(order_related_data.date), 
                                '{}:00-{}:00'.format(order_related_data.start_time, order_related_data.end_time), 
                                '{} {} {}'.format(order_related_data.name, order_related_data.venue_name, order_related_data.stadium_court_name))
                send_email_background(background_tasks, 'Stadium Matching - 訂單取消通知', mail_content, recipients=member_emails)

        return {'message': 'success', 'data': data}
    except Exception as e:
        print('error >>> ', e)

        return {'message': 'fail. error: {}'.format(e)}