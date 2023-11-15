"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime
from typing import List, Optional, Dict, Union, Any

from pydantic import BaseModel, Field
from .user import UserBase

# Shared properties
class StadiumBase(BaseModel):
    #auto increment doesn't need id
    stadium_id: Optional[int] = Field(alias='id') # None

    class Config:
        allow_population_by_field_name = True

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


class StadiumList(StadiumBase):
    name: str
    picture: Optional[str] = None
    area: Optional[float] = None


class StadiumListMessage(BaseModel):
    message: str
    stadium: Optional[List[StadiumList]] = None

class StadiumInfoMessage(BaseModel):
    message: str
    data: Optional[Stadium]

# Additional properties stored in DB

