"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from .stadium import StadiumBase
from datetime import date

# Shared properties
class StadiumDisableBase(BaseModel):
    stadium_id: int

# Properties to receive via API on creation

class StadiumDisableCreate(StadiumDisableBase):
    date: date
    start_time: int
    end_time: int

# Properties to receive via API on update
class StadiumDisableUpdate(StadiumDisableBase):
    date: date
    start_time: int
    end_time: int
    
# Additional properties to return via API

# Disabke return message
class StadiumDisableResponse(BaseModel):
    message: str
    data: Optional[StadiumDisableCreate] = None

    class Config:
        orm_mode = True

# Additional properties stored in DB