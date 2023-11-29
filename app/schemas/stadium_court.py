"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional, Union, Dict

from pydantic import BaseModel, Field
from .stadium import Stadium, StadiumBase, StadiumCreate
from .stadium_available_time import StadiumAvailableTime, StadiumAvailableTimeCreate

# Shared properties
class StadiumCourtBase(BaseModel):
    #auto increment doesn't need id
    stadium_court_id: Optional[int] = Field(validation_alias='id') # None
    name: str
    # max_number_of_people: int

    class Config:
        allow_population_by_field_name = True

# Properties to receive via API on creation
class StadiumCourtCreateList(BaseModel):
    stadium: StadiumCreate
    stadium_available_times: StadiumAvailableTimeCreate
    stadium_court_name: List[str]

class StadiumCourtCreate(BaseModel):
    stadium: StadiumBase
    name: str

# Properties to receive via API on update
class StadiumCourtUpdate(StadiumCourtBase):
    stadium: StadiumBase
    
# Additional properties to return via API

# Additional properties stored in DB
class StadiumCourtInDBBase(StadiumCourtBase):
    stadium: StadiumBase

    class Config:
        orm_mode = True


class StadiumCourt(StadiumCourtInDBBase):
    pass


class StadiumCourtCreateWithMessage(BaseModel):
    message: str
    stadium: Stadium
    stadium_available_times: List[StadiumAvailableTime]
    stadium_court: List[StadiumCourtBase]

# stadium_court_with_rent_info

class StadiumCourtWithRentInfo(StadiumCourtBase):
    # is_matching: Optional[bool] = None
    renter_name: Optional[str] = None
    team_id: Optional[int] = None
    current_member_number: Optional[int] = None
    max_number_of_member: Optional[int] = None
    level_requirement: Optional[List[str]] = None
    status: str

class StadiumCourtWithRentInfoMessage(BaseModel):
    message: str
    data: Optional[List[StadiumCourtWithRentInfo]]