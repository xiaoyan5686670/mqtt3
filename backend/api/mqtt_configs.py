"""MQTT配置相关的API路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.mqtt_config import MQTTConfig, MQTTConfigCreate, MQTTConfigUpdate
from schemas.user import User
from services import mqtt_config_service as mqtt_config_service_module
from api.auth import get_current_active_user, require_admin

router = APIRouter()


@router.get("", response_model=List[MQTTConfig])
def get_mqtt_configs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取MQTT配置列表（仅管理员）"""
    return mqtt_config_service_module.get_mqtt_configs(db, skip=skip, limit=limit)


@router.get("/{config_id}", response_model=MQTTConfig)
def get_mqtt_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取单个MQTT配置（仅管理员）"""
    config = mqtt_config_service_module.get_mqtt_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="MQTT Config not found")
    return config


@router.post("", response_model=MQTTConfig, status_code=status.HTTP_201_CREATED)
def create_mqtt_config(
    config: MQTTConfigCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """创建MQTT配置（仅管理员）"""
    return mqtt_config_service_module.create_mqtt_config(db, config)


@router.put("/{config_id}", response_model=MQTTConfig)
def update_mqtt_config(
    config_id: int, 
    config_update: MQTTConfigUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新MQTT配置（仅管理员）"""
    # 如果请求中包含is_active字段，则调用激活/停用函数
    if config_update.is_active is not None:
        if config_update.is_active:
            success = mqtt_config_service_module.activate_mqtt_config(db, config_id)
        else:
            success = mqtt_config_service_module.deactivate_mqtt_config(db, config_id)
        if not success:
            raise HTTPException(status_code=404, detail="MQTT Config not found")
    
    config = mqtt_config_service_module.update_mqtt_config(db, config_id, config_update)
    if not config:
        raise HTTPException(status_code=404, detail="MQTT Config not found")
    return config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mqtt_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除MQTT配置（仅管理员）"""
    success = mqtt_config_service_module.delete_mqtt_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="MQTT Config not found")
    return None


@router.post("/{config_id}/activate", response_model=MQTTConfig)
def activate_mqtt_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """激活MQTT配置（仅管理员）"""
    success = mqtt_config_service_module.activate_mqtt_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="MQTT Config not found")
    config = mqtt_config_service_module.get_mqtt_config(db, config_id)
    return config