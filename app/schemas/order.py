"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime

from typing import List, Optional

from pydantic import BaseModel, Field

from .stadium_court import StadiumCourtBase

from .user import UserBase


# Shared properties
class OrderBase(BaseModel):
    order_id: int = Field(alias='id')

    class Config:
        allow_population_by_field_name = True


# Properties to receive via API on creation
class OrderCreate(OrderBase):
    stadium_court_id: StadiumCourtBase
    renter_id: UserBase
    datetime: datetime
    start_time: int = None
    end_time: int = None
    status: int = None
    is_matching: bool
    created_time = datetime


# Properties to receive via API on update
class OrderUpdate(OrderBase):
    status: int = None
    is_matching: bool


# Additional properties to return via API


# Additional properties stored in DB
