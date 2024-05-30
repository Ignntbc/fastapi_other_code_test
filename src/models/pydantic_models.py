
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    password: str

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class User_api(UserBase):
    id: int
    is_active: bool
    role: str
    hashed_password: str

    class Config:
        orm_mode = True


class ArticleBase(BaseModel):
    title: str
    content: str
    published_date: Optional[date] = None
    author_id: int

class ArticleCreate(ArticleBase):
    pass

class Article_api(ArticleBase):
    id: int
    

    class Config:
        orm_mode = True