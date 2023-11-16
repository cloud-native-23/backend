"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""

from typing import List, Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    user_id: Optional[int]
    email: Optional[EmailStr] = None
    is_provider: bool = False
    name: Optional[str] = "--"


class UserUpdateNoEmail(BaseModel):
    name: Optional[str] = "--"
    picture: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = None
    picture: Optional[str] = None
    #is_google_sso: Optional[bool] = False


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    line_id: Optional[str]
    picture: Optional[str]

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class UserGetBase(BaseModel):
    email: Optional[EmailStr] = None

    class Config:
        orm_mode = True


class UserCredential(BaseModel):
    name: str
    email: str


class UserMessage(BaseModel):
    message: str
    data: Optional[User] = None


class UsersMessage(BaseModel):
    message: str
    data: Optional[List[User]] = None
