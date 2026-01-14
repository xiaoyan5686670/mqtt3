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
def get_device_publish_topic(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取设备的发布主题（用于继电器控制等）"""
    from core.logging_config import get_logger
    logger = get_logger(__name__)
    
    device = device_service_module.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # 如果设备有关联的主题配置，使用配置的发布主题
    if device.topic_config_id:
        from services import topic_config_service
        logger.debug(f"设备 {device_id} (名称: {device.name}) 关联了 TopicConfig ID: {device.topic_config_id}")
        topic_config = topic_config_service.get_topic_config(db, device.topic_config_id)
        if topic_config:
            logger.debug(f"找到 TopicConfig: ID={topic_config.id}, name={topic_config.name}, publish_topic={topic_config.publish_topic}")
            if topic_config.publish_topic:
                logger.info(f"设备 {device_id} 使用 TopicConfig 配置的发布主题: {topic_config.publish_topic}")
                return {
                    "device_id": device_id,
                    "publish_topic": topic_config.publish_topic,
                    "source": "topic_config"
                }
            else:
                logger.warning(f"设备 {device_id} 的 TopicConfig (ID: {device.topic_config_id}) 没有配置 publish_topic，尝试自动匹配")
        else:
            logger.warning(f"设备 {device_id} 关联的 TopicConfig ID {device.topic_config_id} 不存在，尝试自动匹配")
    
    # 如果设备没有关联 TopicConfig 或关联的 TopicConfig 没有 publish_topic，尝试根据设备名自动匹配
    if device.name:
        from services import topic_config_service
        logger.debug(f"设备 {device_id} (名称: {device.name}) 尝试根据设备名自动匹配 TopicConfig")
        matched_config = topic_config_service.find_topic_config_by_device_name(db, device.name)
        if matched_config:
            logger.debug(f"自动匹配到 TopicConfig: ID={matched_config.id}, name={matched_config.name}, publish_topic={matched_config.publish_topic}")
            if matched_config.publish_topic:
                logger.info(f"设备 {device_id} (名称: {device.name}) 自动匹配到 TopicConfig，使用发布主题: {matched_config.publish_topic}")
                return {
                    "device_id": device_id,
                    "publish_topic": matched_config.publish_topic,
                    "source": "auto_matched_topic_config"
                }
            else:
                logger.debug(f"自动匹配到的 TopicConfig (ID: {matched_config.id}) 没有配置 publish_topic")
        else:
            logger.debug(f"设备 {device_id} (名称: {device.name}) 未能自动匹配到 TopicConfig")
    
    # 如果没有配置，优先使用统一的 "pc/{device_id}" 格式
    # 这样可以确保所有设备使用统一的主题格式，避免因设备名称不同导致主题不一致
    # 注意：如果设备实际固件使用其它主题，请在 TopicConfig 里配置 publish_topic
    default_topic = f"pc/{device_id}"
    
    # 尝试从设备名称提取主题（仅当设备名明确是 pc_* 或 pc/* 格式时才使用）
    if device.name:
        name = device.name.strip().lower()  # 转换为小写以便匹配
        
        # 若设备名本身就是类似 "pc/1" 的主题格式，且以 "pc/" 开头，则直接使用
        if "/" in name and name.startswith("pc/"):
            parts = [p for p in name.split("/") if p]
            if len(parts) >= 2:
                return {
                    "device_id": device_id,
                    "publish_topic": name,  # 保持原始大小写
                    "source": "device_name"
                }

        # 如果设备名称是 pc_* 格式（如 pc_1 -> pc/1），则使用推断的主题
        # 但如果不是 pc_* 格式（如 stm32_1），则使用默认的 pc/{device_id}
        m = re.match(r"^pc[_-](.+)$", name)
        if m:
            inferred_topic = f"pc/{m.group(1)}"
            return {
                "device_id": device_id,
                "publish_topic": inferred_topic,
                "source": "device_name"
            }
    
    # 使用默认主题（统一使用 pc/{device_id} 格式）
    return {
        "device_id": device_id,
        "publish_topic": default_topic,
        "source": "default"
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


@router.get("/{device_id}/latest-sensors", response_model=List[SensorData])
def get_latest_device_sensors(
    device_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取设备的最新传感器数据（需要认证）"""
    sensors = sensor_service_module.get_latest_device_sensors(db, device_id)
    return sensors