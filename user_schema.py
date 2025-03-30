from pydantic import BaseModel
from typing import Optional, Dict

class UserBase(BaseModel):
    name: str
    telefone: str
    details: Optional[Dict] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True
