"""传感器数据相关的API路由"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.sensor import SensorData, SensorDataUpdate
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


@router.put("/{sensor_id}/display-name", response_model=SensorData)
def update_sensor_display_name(
    sensor_id: int, 
    update_data: SensorDataUpdate,
    db: Session = Depends(get_db)
):
    """更新传感器的显示名称"""
    sensor = sensor_service_module.update_sensor_display_name(
        db, sensor_id, update_data.display_name
    )
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.put("/device/{device_id}/type/{sensor_type}/display-name", response_model=SensorData)
def update_sensor_display_name_by_type(
    device_id: int,
    sensor_type: str,
    update_data: SensorDataUpdate,
    db: Session = Depends(get_db)
):
    """根据设备ID和传感器类型更新显示名称（更新该类型的所有传感器）"""
    sensor = sensor_service_module.update_sensor_by_type_and_device(
        db, device_id, sensor_type, update_data.display_name
    )
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor