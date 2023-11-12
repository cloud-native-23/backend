"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from .stadium import StadiumBase

# Shared properties
class StadiumDisableBase(BaseModel):
    stadium: StadiumBase

# Properties to receive via API on creation

class StadiumDisableCreate(StadiumDisableBase):
    datetime: datetime
    start_time: int
    end_time: int

# Properties to receive via API on update
class StadiumDisableUpdate(StadiumDisableBase):
    datetime: datetime
    start_time: int
    end_time: int
    
# Additional properties to return via API

# Additional properties stored in DB