"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""

from typing import List, Optional, Any

from pydantic import BaseModel, Field

from .order import OrderBase

from .user import UserCredential

# Shared properties
class TeamBase(BaseModel):
    team_id: int = Field(alias='id')

    class Config:
        allow_population_by_field_name = True


# Properties to receive via API on creation
class TeamCreate(TeamBase):
    order_id: OrderBase
    max_number_of_member: int = None
    current_member_number: int = None
    level_requirement: Optional[int] = None


# Properties to receive via API on update
class TeamUpdate(TeamBase):
    max_number_of_member: int = None
    current_member_number: int = None
    level_requirement: Optional[int] = None

class TeamJointListResponse(BaseModel):
    team_joint_list: List[dict]

class TeamJoinInfo(BaseModel):
    team_id: int
    team_member_emails: Optional[List[str]]

class TeamWithTeamMemberInfo(TeamCreate):
    order_id: int
    team_members: Optional[List[UserCredential]]

class TeamWithTeamMemberInfoMessage(BaseModel):
    message: str
    data: Optional[TeamWithTeamMemberInfo]

# Additional properties to return via API


# Additional properties stored in DB
