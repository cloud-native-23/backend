"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime, date

from typing import List, Optional

from pydantic import BaseModel, Field

from .stadium_court import StadiumCourtBase

from .user import UserBase, UserCredential


# Shared properties
class OrderBase(BaseModel):
    order_id: int = Field(alias='id')

    class Config:
        allow_population_by_field_name = True


# Properties to receive via API on creation
class OrderCreateInfo(OrderBase):
    stadium_court_id: int
    renter_id: int
    start_time: int = None
    end_time: int = None
    status: int = None
    is_matching: bool
    created_time = datetime
    date: date

class OrderCreate(BaseModel):
    stadium_court_id: int
    renter_id: int
    start_time: int = None
    end_time: int = None
    status: int = None
    is_matching: bool
    date: date


# Properties to receive via API on update
class OrderUpdate(OrderBase):
    status: int = None
    is_matching: bool

class OrderRentInfo(OrderBase):
    order_time: date
    start_time: int = None
    end_time: int = None
    stadium_name: str
    venue_name: str
    court_name: str
    status: str = None
    current_member_number: int
    max_number_of_member: int
    team_members: Optional[List[UserCredential]] = None
    

class OrderRentResponse(BaseModel):
    orders: List[OrderRentInfo]

class OrderCancelResponse(BaseModel):
    message: str
    order: OrderCreateInfo

class OrderCreateWithTeamInfo(BaseModel):
    stadium_court_id: int
    date: date
    start_time: int
    end_time: int
    current_member_number: int
    max_number_of_member: int
    is_matching: bool
    level_requirement: List[str]
    team_member_emails: Optional[List[str]]

class OrderWithTeamInfo(OrderCreateWithTeamInfo):
    id: int
    team_id: int
    team_members: List[UserCredential]

class OrderWithTeamInfoMessage(BaseModel):
    message: str
    data: Optional[OrderWithTeamInfo]


# Additional properties to return via API


# Additional properties stored in DB
