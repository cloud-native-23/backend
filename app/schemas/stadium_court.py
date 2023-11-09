"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from .stadium import StadiumBase

# Shared properties
class StadiumCourtBase(BaseModel):
    stadium_court_id: int

# Properties to receive via API on creation

class StadiumCourtCreate(StadiumCourtBase):
    name: str
    max_number_of_people: int
    stadium: StadiumBase

# Properties to receive via API on update
class StadiumCourtUpdate(StadiumCourtBase):
    name: str
    max_number_of_people: int
    stadium: StadiumBase
    
# Additional properties to return via API

# Additional properties stored in DB