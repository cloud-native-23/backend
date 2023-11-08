"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from .stadium import UserBase

# Shared properties
class StadiumBase(BaseModel):
    stadium_id: str

# Properties to receive via API on creation
class StadiumCreate(StadiumBase): 
    name: str
    address: Optional[str] = None
    picture: Optional[str] = None
    area: Optional[float] = None
    description: Optional[str] = None
    created_user: UserBase

# Properties to receive via API on update
class StadiumUpdate(StadiumBase):
    name: str
    address: Optional[str] = None
    picture: Optional[str] = None
    area: Optional[float] = None
    description: Optional[str] = None

# Additional properties to return via API

# Additional properties stored in DB