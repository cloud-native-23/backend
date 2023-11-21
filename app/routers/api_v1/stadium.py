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


@router.get("/timetable/", response_model=schemas.StadiumAvailabilityResponse)
def get_stadium_availability(
    stadium_id: int,
    query_date: str,
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
                    db=db, stadium_id=stadium_id, date=current_date, start_time=start_time, end_time=end_time
                )

                if is_disabled:
                    availability_data["day_{}".format(i + 1)][str(start_time)] = "Disabled"
                else:
                    # Check if the court is booked at this time
                    # 看該時段之下，該stadium之下的所有stadium court是否被借走
                    # 如果至少還有一個可以被租借（沒有order紀錄）則 Available
                    is_booked = crud.order.is_booked(
                        db=db, stadium_id=stadium_id, date=current_date, start_time=start_time, end_time=end_time
                    )

                    if is_booked:
                        availability_data["day_{}".format(i + 1)][str(start_time)] = "Booked"
                    else:
                        availability_data["day_{}".format(i + 1)][str(start_time)] = "Available"
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
            stadium_courts.append(stadium_court)
        
        # Create StadiumAvailableTimes
        stadium_available_times = []
        for stadium_available_time_weekday in stadium_court_in.stadium_available_times.weekday:
            stadium_available_time = crud.stadium_available_time.create(db=db, obj_in=stadium_court_in.stadium_available_times, weekday=stadium_available_time_weekday,stadium_id=stadium.id)
            stadium_available_times.append(stadium_available_time.to_dict())

        # Adjust the response to include stadium, StadiumAvailableTimes and stadium courts
        return {"message": "success", "stadium": stadium, "stadium_available_times": [time for time in stadium_available_times], "stadium_courts": [court for court in stadium_courts]}

    except Exception as e:
        print('Error:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stadium-list/", response_model=schemas.stadium.StadiumListMessage)
def get_stadium_list_with_created_user(
    created_user: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    # TODO: wait for user validation
    # current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve stadium list w/ or w/o created_user.
    """
    try:
        
        stadiums = crud.stadium.get_stadium_list(
        db=db, user_id=created_user
        )

        stadiums_data = [
            {'stadium_id': stadium_id, 'name': name, 'picture': picture, 'area': area}
            for stadium_id, name, picture, area in stadiums
        ]
        return {"message": "success", "stadium": stadiums_data}
    
    except Exception as e:
        print('Error:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/info", response_model=schemas.stadium.StadiumInfoMessage)
def get_stadium(
    stadium_id: int,
    db: Session = Depends(deps.get_db),
    # TODO: wait for user validation
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
    stadium_available_times_dict = [x.to_dict() for x in stadium_available_times]
    data = schemas.StadiumInfo(
        stadium_id = stadium.id,
        name = stadium.name,
        address = stadium.address,
        picture = stadium.picture,
        area = stadium.area,
        description = stadium.description,
        created_user = stadium.created_user,
        max_number_of_people = stadium_courts[0].max_number_of_people if len(stadium_courts) > 0 else None,
        number_of_court = len(stadium_courts),
        available_times = stadium_available_times_dict
    )

    return {"message": "success", "data": data}

@router.delete("/delete", response_model=schemas.stadium.StadiumDeleteMessage)
def delete_stadium(
    stadium_id: int,
    db: Session = Depends(deps.get_db),
    # TODO: wait for user validation
    # current_user: models.user = Depends(deps.get_current_active_user),
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
    stadium_disable = crud.stadium_disable.is_disabled(
        db=db, stadium_id=StadiumDisableCreate_in.stadium_id, date=StadiumDisableCreate_in.date, start_time=StadiumDisableCreate_in.start_time, end_time=StadiumDisableCreate_in.end_time
    )
    if stadium_disable:
        raise HTTPException(
            status_code=400,
            detail="Stadium is already disabled at the time.",
        )
    isDisableSuccessfully = crud.stadium_disable.create(db=db, obj_in=StadiumDisableCreate_in)
    if isDisableSuccessfully:
        return {'message': 'success', 'data': StadiumDisableCreate_in}
    else:
        return {'message': 'fail', 'data': StadiumDisableCreate_in}