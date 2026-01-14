"""设备相关的Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeviceBase(BaseModel):
    name: str
    display_name: Optional[str] = None  # 展示名称，用于首页显示
    device_type: str
    location: Optional[str] = None
    remark: Optional[str] = None  # 备注字段
    show_on_dashboard: Optional[bool] = True  # 是否在首页展示


class DeviceCreate(DeviceBase):
    mqtt_config_id: Optional[int] = None
    topic_config_id: Optional[int] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None  # 展示名称，用于首页显示
    device_type: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    remark: Optional[str] = None  # 备注字段
    show_on_dashboard: Optional[bool] = None  # 是否在首页展示
    mqtt_config_id: Optional[int] = None
    topic_config_id: Optional[int] = None


class Device(DeviceBase):
    id: int
    status: str
    display_name: Optional[str] = None  # 展示名称，用于首页显示
    remark: Optional[str] = None  # 备注字段
    show_on_dashboard: bool = True  # 是否在首页展示
    mqtt_config_id: Optional[int] = None
    topic_config_id: Optional[int] = None
    created_at: datetime  # 设备创建时间

    class Config:
        from_attributes = True