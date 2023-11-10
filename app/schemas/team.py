"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""

from typing import List, Optional

from pydantic import BaseModel

from .order import OrderBase

# Shared properties
class TeamBase(BaseModel):
    team_id: int


# Properties to receive via API on creation
class TeamCreate(TeamBase):
    order_id: OrderBase
    max_number_of_member: int = None
    orig_member_number: int = None
    level_requirement: Optional[int] = None


# Properties to receive via API on update
class TeamUpdate(TeamBase):
    max_number_of_member: int = None
    orig_member_number: int = None
    level_requirement: Optional[int] = None


# Additional properties to return via API


# Additional properties stored in DB
