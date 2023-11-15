"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""
from datetime import datetime

from typing import List, Optional

from pydantic import BaseModel, Field

from .user import UserBase

from .team import TeamBase

# Shared properties
class TeamMemberBase(BaseModel):
    pass


# Properties to receive via API on creation
class TeamMemberCreate(TeamMemberBase):
    team_member_id: int = Field(alias='id')
    team_id: TeamBase
    user_id: UserBase

    class Config:
        allow_population_by_field_name = True


# Properties to receive via API on update
class TeamMemberUpdate(TeamMemberBase):
    pass


# Additional properties to return via API


# Additional properties stored in DB
