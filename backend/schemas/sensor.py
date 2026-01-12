"""传感器数据相关的Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SensorDataBase(BaseModel):
    device_id: int
    type: str
    value: float
    unit: str


class SensorDataCreate(SensorDataBase):
    pass


class SensorData(SensorDataBase):
    id: int
    timestamp: datetime
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    alert_status: Optional[str] = None

    class Config:
        from_attributes = True