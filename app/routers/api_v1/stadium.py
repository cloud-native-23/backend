import json
from typing import Any
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
    # current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new stadium.
    """ 
    try:

        # Create Stadium
        stadium = crud.stadium.create(db=db, obj_in=stadium_court_in.stadium)

        # Create StadiumCourts
        stadium_courts = []
        for stadium_court_data in stadium_court_in.data:
            # Associate with the created stadium
            stadium_court = crud.stadium_court.create(db=db, obj_in=stadium_court_data, stadium_id=stadium.id)
            stadium_courts.append(stadium_court)

        # Adjust the response to include both stadium and stadium courts
        return {"message": "success", "stadium": stadium_court_in.stadium, "stadium_courts": [court for court in stadium_court_in.data]}

    except Exception as e:
        print('Error:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


