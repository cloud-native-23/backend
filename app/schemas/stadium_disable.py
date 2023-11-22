"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel
from .stadium import StadiumBase
from datetime import date

# Shared properties
class StadiumDisableBase(BaseModel):
    stadium_id: int

# Properties to receive via API on creation

class StadiumDisableSessions(BaseModel):
    date: date
    start_time: int

class StadiumDisableCreate(StadiumDisableBase):
    sessions: List[StadiumDisableSessions]

# Properties to receive via API on update
class StadiumDisableUpdate(StadiumDisableBase):
    date: date
    start_time: int
    end_time: int
    
# Additional properties stored in DB

class StadiumDisableInDBBase(StadiumDisableBase):
    date: date
    start_time: int
    end_time: int

    class Config:
        orm_mode = True

# Additional properties to return via API

# Disable return message
class StadiumDisableResponse(BaseModel):
    message: str
    data: Optional[StadiumDisableCreate] = None