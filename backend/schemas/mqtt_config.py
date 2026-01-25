"""MQTT配置相关的Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional


class MQTTConfigBase(BaseModel):
    name: str
    server: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None


class MQTTConfigCreate(MQTTConfigBase):
    pass


class MQTTConfigUpdate(BaseModel):
    name: Optional[str] = None
    server: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    api_port: Optional[int] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None


class MQTTConfig(MQTTConfigBase):
    id: int
    is_active: bool = False
    api_port: Optional[int] = 18083
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    user_id: Optional[int] = None  # 所属用户ID，None表示系统级配置

    class Config:
        from_attributes = True