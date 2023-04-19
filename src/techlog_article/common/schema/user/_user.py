from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class UserCore(BaseModel):
    username: str
    email: str

    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]


class User(UserCore):
    id: UUID = Field(
        description="The primary key that is automatically generated from the DB"
    )


class UserInDB(User):
    hashed_password: str = Field(
        description="The hashed password to be stored in the DB"
    )


class Admin(User):
    pass