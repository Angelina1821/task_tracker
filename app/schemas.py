from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    name: str = Field(..., max_length=100)
    login: str = Field(..., max_length=30)
    password: str = Field(..., min_length=6)
    role_id: int = 2 #user

class UserLogin(BaseModel):
    login: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    name: str
    login: str
    role_id: int
    last_active: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    deadline: Optional[str] = None
    descr: Optional[str] = None
    categ_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    deadline: Optional[datetime] = None
    descr: Optional[str] = None
    categ_id: Optional[int] = None
    status_id: Optional[int] = None

class TaskResponse(BaseModel):
    task_id: int
    user_id: int
    categ_id: Optional[int] = None
    created: Optional[datetime]
    deadline: Optional[datetime] = None
    status_id: Optional[int]
    title: str
    descr: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    title: str = Field(..., max_length=100)

class CategoryResponse(BaseModel):
    categ_id: int
    title: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token:str
    token_type: str

class TokenData(BaseModel):
    login: str

class StatusStats(BaseModel):
    status_id: int
    status_title: str
    count: int

class CategoryStats:
    categ_title: str
    task_count: int
