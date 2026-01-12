"""传感器数据相关的API路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.sensor import SensorData
from services import sensor_service as sensor_service_module

router = APIRouter()


@router.get("/device/{device_id}", response_model=List[SensorData])
def get_device_sensors(device_id: int, db: Session = Depends(get_db)):
    """获取设备的所有传感器数据"""
    sensors = sensor_service_module.get_device_sensors(db, device_id)
    return sensors


@router.get("/device/{device_id}/latest", response_model=List[SensorData])
def get_latest_device_sensors(device_id: int, db: Session = Depends(get_db)):
    """获取设备的最新传感器数据（按类型分组）"""
    sensors = sensor_service_module.get_latest_device_sensors(db, device_id)
    return sensors


@router.get("/latest", response_model=List[SensorData])
def get_latest_sensors(limit: int = 50, db: Session = Depends(get_db)):
    """获取最新的传感器数据"""
    sensors = sensor_service_module.get_latest_sensors(db, limit=limit)
    return sensors