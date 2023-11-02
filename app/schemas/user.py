"""
BaseModel.schema will return a dict of the schema
while BaseModel.schema_json will return a JSON string representation of that dict.
"""

from typing import List, Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_admin: bool = False
    name: Optional[str] = "--"


class UserUpdateNoEmail(BaseModel):
    name: Optional[str] = "--"
    line_id: Optional[str] = None
    image: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = None
    line_id: Optional[str] = None
    image: Optional[str] = None
    is_google_sso: Optional[bool] = False


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    line_id: Optional[str]
    image: Optional[str]

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
    credential: str


class UserMessage(BaseModel):
    message: str
    data: Optional[User] = None


class UsersMessage(BaseModel):
    message: str
    data: Optional[List[User]] = None
