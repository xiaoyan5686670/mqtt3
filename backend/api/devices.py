"""设备相关的API路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.device import Device, DeviceCreate, DeviceUpdate
from services import device_service as device_service_module
from schemas.sensor import SensorData
from services import sensor_service as sensor_service_module


router = APIRouter()


@router.get("", response_model=List[Device])
def get_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取设备列表"""
    devices = device_service_module.get_devices(db, skip=skip, limit=limit)
    return devices


@router.get("/{device_id}", response_model=Device)
def get_device(device_id: int, db: Session = Depends(get_db)):
    """获取单个设备"""
    device = device_service_module.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("", response_model=Device, status_code=status.HTTP_201_CREATED)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """创建设备"""
    return device_service_module.create_device(db, device)


@router.put("/{device_id}", response_model=Device)
def update_device(device_id: int, device_update: DeviceUpdate, db: Session = Depends(get_db)):
    """更新设备"""
    device = device_service_module.update_device(db, device_id, device_update)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: int, db: Session = Depends(get_db)):
    """删除设备"""
    success = device_service_module.delete_device(db, device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return None


@router.get("/{device_id}/latest-sensors", response_model=List[SensorData])
def get_latest_device_sensors(device_id: int, db: Session = Depends(get_db)):
    """获取设备的最新传感器数据"""
    sensors = sensor_service_module.get_latest_device_sensors(db, device_id)
    return sensors