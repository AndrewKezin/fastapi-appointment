from pydantic import BaseModel, EmailStr
from enum import Enum, auto

class UserRole(Enum):
    USER = auto()
    ADMIN = auto()



class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    middle_name: str | None
    last_name: str
    phone: str
    address: str

class UserCreate(UserBase):
    password: str

class UserCheckRole(UserBase):
    role: UserRole = UserRole.USER

class UserResponse(UserBase):
    id: str
    is_active: bool


    class Config:
        from_attributes = True