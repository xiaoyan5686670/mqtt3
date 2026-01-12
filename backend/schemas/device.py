"""设备相关的Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeviceBase(BaseModel):
    name: str
    device_type: str
    location: Optional[str] = None
    remark: Optional[str] = None  # 备注字段


class DeviceCreate(DeviceBase):
    mqtt_config_id: Optional[int] = None
    topic_config_id: Optional[int] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    device_type: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    remark: Optional[str] = None  # 备注字段
    mqtt_config_id: Optional[int] = None
    topic_config_id: Optional[int] = None


class Device(DeviceBase):
    id: int
    status: str
    remark: Optional[str] = None  # 备注字段
    mqtt_config_id: Optional[int] = None
    topic_config_id: Optional[int] = None
    created_at: datetime  # 设备创建时间

    class Config:
        from_attributes = True