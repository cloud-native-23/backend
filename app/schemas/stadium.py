"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional, Dict, Union, Any

from pydantic import BaseModel, Field
from .user import UserBase

# Shared properties
class StadiumBase(BaseModel):
    #auto increment doesn't need id
    stadium_id: Optional[int] = Field(alias='id') # None

    class Config:
        allow_population_by_field_name = True

# Properties to receive via API on creation
class StadiumCreate(StadiumBase): 
    name: str
    venue_name: str
    address: Optional[str] = None
    picture: Optional[str] = None
    area: Optional[float] = None
    description: Optional[str] = None
    # created_user: int
    max_number_of_people: int
    google_map_url: Optional[str] = None

# Properties to receive via API on update
class StadiumUpdate(StadiumBase):
    name: str
    venue_name: str
    address: Optional[str] = None
    picture: Optional[str] = None
    area: Optional[float] = None
    description: Optional[str] = None
    max_number_of_people: int
    google_map_url: Optional[str] = None

# Additional properties to return via API
class StadiumAvailabilityResponse(StadiumBase): 
    query_date: datetime
    message: str
    data: Any

    class Config:
        arbitrary_types_allowed = True


class StadiumInDBBase(StadiumBase):
    name: str
    venue_name: str
    address: Optional[str] = None
    picture: Optional[str] = None
    area: Optional[float] = None
    description: Optional[str] = None
    created_user: int
    max_number_of_people: int
    google_map_url: Optional[str] = None

    class Config:
        orm_mode = True


class Stadium(StadiumInDBBase):
    pass


class StadiumList(StadiumBase):
    name: str
    venue_name: str
    picture: Optional[str] = None
    area: Optional[float] = None
    max_number_of_people: Optional[int] = None
    current_people_count: Optional[int] = None
    google_map_url: Optional[str] = None


class StadiumListMessage(BaseModel):
    message: str
    stadium: Optional[List[StadiumList]] = None

# define in this file to avoid circular import
class StadiumCourtForInfo(BaseModel):
    id: Optional[int] # optional for add new stadium_court when update stadium
    name: str

class StadiumAvailableTimeForInfo(BaseModel):
    weekdays: Optional[List[int]] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None

class StadiumInfo(Stadium):
    max_number_of_people: Optional[int]
    stadium_courts: List[StadiumCourtForInfo]
    available_times: StadiumAvailableTimeForInfo

class StadiumInfoMessage(BaseModel):
    message: str
    data: Optional[StadiumInfo]

class StadiumUpdateAdditionalInfo(StadiumUpdate):
    stadium_courts: List[StadiumCourtForInfo]
    available_times: StadiumAvailableTimeForInfo

class StadiumDeleteMessage(BaseModel):
    message: str
    data: Optional[Stadium] = None

# Additional properties stored in DB

