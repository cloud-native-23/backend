"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional, Dict, Union, Any

from pydantic import BaseModel
from .user import UserBase

# Shared properties
class StadiumBase(BaseModel):
    #auto increment doesn't need id
    stadium_id: Optional[int] = None

# Properties to receive via API on creation
class StadiumCreate(StadiumBase): 
    name: str
    address: Optional[str] = None
    picture: Optional[str] = None
    area: Optional[float] = None
    description: Optional[str] = None
    created_user: int

# Properties to receive via API on update
class StadiumUpdate(StadiumBase):
    name: str
    address: Optional[str] = None
    picture: Optional[str] = None
    area: Optional[float] = None
    description: Optional[str] = None

# Additional properties to return via API
class StadiumAvailabilityResponse(StadiumBase): 
    query_date: datetime
    message: str
    data: Any

    class Config:
        arbitrary_types_allowed = True


class StadiumInDBBase(StadiumBase):
    name: str
    address: Optional[str] = None
    picture: Optional[str] = None
    area: Optional[float] = None
    description: Optional[str] = None
    created_user: int

    class Config:
        orm_mode = True


class Stadium(StadiumInDBBase):
    pass

class StadiumListMessage(BaseModel):
    message: str
    stadium: List[Stadium]

# Additional properties stored in DB

