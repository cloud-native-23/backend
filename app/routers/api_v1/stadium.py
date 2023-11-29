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


@router.post("/timetable/", response_model=schemas.StadiumAvailabilityResponse)
def get_stadium_availability(
    stadium_id: int,
    query_date: str,
    headcount:int,
    level_requirement:int,
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
                    headcount_and_level_checking_result = crud.order.headcount_and_level_requirement_checking(
                        db=db, stadium_id=stadium_id, current_date=current_date, start_time=start_time, headcount= headcount, level_requirement = level_requirement
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
    if stadium_id is None:
        raise HTTPException(
            status_code=400,
            detail="Fail to get stadium info. Missing parameter: stadium_id.",
        )
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
    if (stadium_id == '' or stadium_id is None):
        raise HTTPException(
            status_code=400,
            detail="Fail to delete stadium. Missing parameter: stadium_id"
        )
    stadium = crud.stadium.get_by_stadium_id(
        db=db, stadium_id=stadium_id)
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
    StadiumDisableCreate_in: schemas.stadium_disable.StadiumDisableCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Disable stadium with stadium_id.
    """
    if (StadiumDisableCreate_in.stadium_id == '' or StadiumDisableCreate_in.stadium_id is None):
        raise HTTPException(
            status_code=400,
            detail="Fail to disable stadium. Missing parameter: stadium_id"
        )
    
    stadium = crud.stadium.get_by_stadium_id(
        db=db, stadium_id=StadiumDisableCreate_in.stadium_id)
    if not stadium:
        raise HTTPException(
            status_code=400,
            detail="No stadium to disable.",
        )
    
    for session in StadiumDisableCreate_in.sessions:
        stadium_disable = crud.stadium_disable.is_disabled(
            db=db, stadium_id=StadiumDisableCreate_in.stadium_id, date=session.date, start_time=session.start_time
        )
        if stadium_disable:
            raise HTTPException(
                status_code=400,
                detail=f"Stadium is already disabled at the time.  Stadium ID: {StadiumDisableCreate_in.stadium_id}, Date: {session.date}, Start Time: {session.start_time}",
            )
        
    isDisableSuccessfully = crud.stadium_disable.create(db=db, obj_in=StadiumDisableCreate_in)
    if isDisableSuccessfully:
        return {'message': 'success', 'data': StadiumDisableCreate_in}
    else:
        return {'message': 'fail', 'data': StadiumDisableCreate_in}
    
@router.delete("/undisable", response_model=schemas.stadium_disable.StadiumDisableResponse)
def disable_stadium(
    StadiumUndisableCreate_in: schemas.stadium_disable.StadiumDisableCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Undisable stadium.
    """
    if (StadiumUndisableCreate_in.stadium_id == '' or StadiumUndisableCreate_in.stadium_id is None):
        raise HTTPException(
            status_code=400,
            detail="Fail to undisable stadium. Missing parameter: stadium_id"
        )
    
    stadium = crud.stadium.get_by_stadium_id(
        db=db, stadium_id=StadiumUndisableCreate_in.stadium_id)
    if not stadium:
        raise HTTPException(
            status_code=400,
            detail="No stadium to undisable.",
        )
    
    for session in StadiumUndisableCreate_in.sessions:
        stadium_disable = crud.stadium_disable.is_disabled(
            db=db, stadium_id=StadiumUndisableCreate_in.stadium_id, date=session.date, start_time=session.start_time
        )
        if not stadium_disable:
            raise HTTPException(
                status_code=400,
                detail=f"Stadium is not disabled at the specified time. Stadium ID: {StadiumUndisableCreate_in.stadium_id}, Date: {session.date}, Start Time: {session.start_time}",
            )
        
        isUndisableSuccessfully = crud.stadium_disable.delete_by_stadium_id_and_session(
            db=db, stadium_id=StadiumUndisableCreate_in.stadium_id, date=session.date, start_time=session.start_time
        )
        if not isUndisableSuccessfully:
            raise HTTPException(
                status_code=400,
                detail=f"Fail to undisable stadium. Stadium ID: {StadiumUndisableCreate_in.stadium_id}, Date: {session.date}, Start Time: {session.start_time}",
            )
        
    return {'message': 'success', 'data': StadiumUndisableCreate_in}

@router.put("/", response_model=schemas.stadium.StadiumInfoMessage)
def update_stadium(
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
        # TODO: what if provider remove a court already reserved ???
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
                create_stadium_court = models.stadium_court.StadiumCourt(
                    stadium_id = orig_stadium.id,
                    name = stadium_court_in.name
                )
                db.add(create_stadium_court)
            else:
                court = crud.stadium_court.get_by_stadium_court_id(db=db, stadium_court_id=stadium_court_in.id)
                # if not in db => new add
                if court is None:
                    create_stadium_court = models.stadium_court.StadiumCourt(
                        stadium_id = orig_stadium.id,
                        name = stadium_court_in.name
                    )
                    db.add(create_stadium_court)
                else: # update
                    court.name = stadium_court_in.name
                    db.add(court)
        # stadium_courts in db but not in api input => delete
        db_stadium_courts = crud.stadium_court.get_all_by_stadium_id(db=db, stadium_id=stadium_obj_in.stadium_id)
        stadium_courts_to_delete = [x for x in db_stadium_courts if x.id not in [y.id for y in stadium_obj_in.stadium_courts]]
        for delete_court in stadium_courts_to_delete:
            db.delete(delete_court)
        ### update stadium_available_times ###
        update_available_times = stadium_obj_in.available_times
        # delete all first
        db.query(models.stadium_available_time.StadiumAvailableTime).filter(models.stadium_available_time.StadiumAvailableTime.stadium_id == stadium_obj_in.stadium_id).delete()
        # create new available_times
        for weekday in update_available_times.weekdays:
            create_available_time = models.stadium_available_time.StadiumAvailableTime(
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

        return {'message': 'success', 'data': data}
    except Exception as e:
        print('error >>> ', e)

        return {'message': 'fail. error: {}'.format(e)}