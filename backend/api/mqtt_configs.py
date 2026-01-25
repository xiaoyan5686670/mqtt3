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
    current_user: User = Depends(get_current_active_user)
):
    """获取MQTT配置列表
    - 管理员：可以查看所有配置
    - 普通用户：只能查看自己的配置
    """
    user_id = None if current_user.is_admin else current_user.id
    return mqtt_config_service_module.get_mqtt_configs(db, skip=skip, limit=limit, user_id=user_id)


@router.get("/{config_id}", response_model=MQTTConfig)
def get_mqtt_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取单个MQTT配置
    - 管理员：可以查看任何配置
    - 普通用户：只能查看自己的配置
    """
    user_id = None if current_user.is_admin else current_user.id
    config = mqtt_config_service_module.get_mqtt_config(db, config_id, user_id=user_id)
    if not config:
        raise HTTPException(status_code=404, detail="MQTT Config not found")
    return config


@router.post("", response_model=MQTTConfig, status_code=status.HTTP_201_CREATED)
def create_mqtt_config(
    config: MQTTConfigCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建MQTT配置
    - 管理员：可以创建系统级配置（user_id=None）或用户配置
    - 普通用户：只能为自己创建配置
    """
    try:
        # 普通用户只能为自己创建，管理员可以创建系统级配置（通过不传user_id）
        user_id = current_user.id
        return mqtt_config_service_module.create_mqtt_config(db, config, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{config_id}", response_model=MQTTConfig)
def update_mqtt_config(
    config_id: int, 
    config_update: MQTTConfigUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新MQTT配置
    - 管理员：可以更新任何配置
    - 普通用户：只能更新自己的配置
    """
    # 权限检查
    user_id = None if current_user.is_admin else current_user.id
    existing_config = mqtt_config_service_module.get_mqtt_config(db, config_id, user_id=user_id)
    if not existing_config:
        raise HTTPException(status_code=404, detail="MQTT Config not found")
    
    # 如果请求中包含is_active字段，则调用激活/停用函数
    if config_update.is_active is not None:
        if config_update.is_active:
            success = mqtt_config_service_module.activate_mqtt_config(db, config_id)
        else:
            success = mqtt_config_service_module.deactivate_mqtt_config(db, config_id)
        if not success:
            raise HTTPException(status_code=404, detail="MQTT Config not found")
    
    try:
        config = mqtt_config_service_module.update_mqtt_config(db, config_id, config_update)
        if not config:
            raise HTTPException(status_code=404, detail="MQTT Config not found")
        return config
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mqtt_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除MQTT配置
    - 管理员：可以删除任何配置
    - 普通用户：只能删除自己的配置
    """
    # 权限检查
    user_id = None if current_user.is_admin else current_user.id
    existing_config = mqtt_config_service_module.get_mqtt_config(db, config_id, user_id=user_id)
    if not existing_config:
        raise HTTPException(status_code=404, detail="MQTT Config not found")
    
    success = mqtt_config_service_module.delete_mqtt_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="MQTT Config not found")
    return None


@router.post("/{config_id}/activate", response_model=MQTTConfig)
def activate_mqtt_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """激活MQTT配置
    - 管理员：可以激活任何配置
    - 普通用户：只能激活自己的配置
    """
    # 权限检查
    user_id = None if current_user.is_admin else current_user.id
    existing_config = mqtt_config_service_module.get_mqtt_config(db, config_id, user_id=user_id)
    if not existing_config:
        raise HTTPException(status_code=404, detail="MQTT Config not found")
    
    success = mqtt_config_service_module.activate_mqtt_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="MQTT Config not found")
    config = mqtt_config_service_module.get_mqtt_config(db, config_id)
    return config