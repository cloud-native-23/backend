"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from .stadium import StadiumBase

# Shared properties
class StadiumAvailableTimeBase(BaseModel):
    stadium_available_id: int = Field(alias='id')
    stadium: StadiumBase

    class Config:
        allow_population_by_field_name = True

# Properties to receive via API on creation

class StadiumAvailableTimeCreate(StadiumAvailableTimeBase):
    weekday: int
    start_time: int
    end_time: int

# Properties to receive via API on update
class StadiumAvailableTimeUpdate(StadiumAvailableTimeBase):
    weekday: int
    start_time: int
    end_time: int
    
# Additional properties to return via API

# Additional properties stored in DB