"""用户相关的Pydantic schemas"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """验证邮箱格式"""
        if v is None or v == '':
            return None
        # 简单的邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class UserCreate(UserBase):
    """创建用户模型"""
    password: str


class UserUpdate(BaseModel):
    """更新用户模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """验证邮箱格式"""
        if v is None or v == '':
            return None
        # 简单的邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class User(UserBase):
    """用户响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: User
