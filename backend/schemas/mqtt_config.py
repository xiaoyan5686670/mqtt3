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


class MQTTConfig(MQTTConfigBase):
    id: int
    is_active: bool = False

    class Config:
        from_attributes = True