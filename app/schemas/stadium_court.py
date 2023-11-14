"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional, Union, Dict

from pydantic import BaseModel
from .stadium import Stadium, StadiumBase, StadiumCreate

# Shared properties
class StadiumCourtBase(BaseModel):
    #auto increment doesn't need id
    stadium_court_id: Optional[int] = None
    name: str
    max_number_of_people: int

# Properties to receive via API on creation
class StadiumCourtCreateList(BaseModel):
    stadium: StadiumCreate

    data: List[StadiumCourtBase]

class StadiumCourtCreate(BaseModel):
    stadium: StadiumBase
    name: str
    max_number_of_people: int

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
    stadium_courts: List[StadiumCourtBase]