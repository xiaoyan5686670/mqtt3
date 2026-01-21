"""设备相关的API路由"""
from typing import List, Optional
import re
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.device import Device, DeviceCreate, DeviceUpdate
from schemas.user import User
from services import device_service as device_service_module
from schemas.sensor import SensorData
from services import sensor_service as sensor_service_module
from api.auth import get_current_active_user, require_admin

router = APIRouter()


def require_admin_or_readonly(current_user: User = Depends(get_current_active_user)):
    """要求管理员权限或只读权限"""
    return current_user


@router.get("", response_model=List[Device])
def get_devices(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取设备列表（需要认证）"""
    devices = device_service_module.get_devices(db, skip=skip, limit=limit)
    return devices


@router.get("/{device_id}", response_model=Device)
def get_device(
    device_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取单个设备（需要认证）"""
    device = device_service_module.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.get("/{device_id}/publish-topic")
def get_device_publish_topic_api(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取设备的发布主题（用于继电器控制等）"""
    device = device_service_module.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {
        "device_id": device_id,
        "publish_topic": device.publish_topic,
        "source": "calculated"
    }


@router.post("", response_model=Device, status_code=status.HTTP_201_CREATED)
def create_device(
    device: DeviceCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """创建设备（仅管理员）"""
    return device_service_module.create_device(db, device)


@router.put("/{device_id}", response_model=Device)
def update_device(
    device_id: int, 
    device_update: DeviceUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新设备（仅管理员）"""
    device = device_service_module.update_device(db, device_id, device_update)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除设备（仅管理员）"""
    success = device_service_module.delete_device(db, device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return None


class DeviceDisplayNameUpdate(BaseModel):
    display_name: Optional[str] = None


class RelayInDisplayNameUpdate(BaseModel):
    relay_in_display_name: Optional[str] = None


@router.put("/{device_id}/display-name", response_model=Device)
def update_device_display_name(
    device_id: int,
    update_data: DeviceDisplayNameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新设备的展示名称（仅管理员）"""
    device = device_service_module.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # 只更新 display_name 字段，不修改 name 字段
    device_update = DeviceUpdate(display_name=update_data.display_name)
    updated_device = device_service_module.update_device(db, device_id, device_update)
    return updated_device


@router.put("/{device_id}/relay-in-display-name", response_model=Device)
def update_relay_in_display_name(
    device_id: int,
    update_data: RelayInDisplayNameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新设备的继电器输入显示名称（仅管理员）"""
    device = device_service_module.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # 更新 relay_in_display_name 字段
    device_update = DeviceUpdate(relay_in_display_name=update_data.relay_in_display_name)
    updated_device = device_service_module.update_device(db, device_id, device_update)
    return updated_device


@router.get("/{device_id}/latest-sensors", response_model=List[SensorData])
def get_latest_device_sensors(
    device_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取设备的最新传感器数据（需要认证）"""
    sensors = sensor_service_module.get_latest_device_sensors(db, device_id)
    return sensors