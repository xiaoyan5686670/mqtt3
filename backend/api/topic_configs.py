"""主题配置相关的API路由"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.topic_config import TopicConfig, TopicConfigCreate, TopicConfigUpdate
from schemas.user import User
from services import topic_config_service as topic_config_service_module
from api.auth import get_current_active_user, require_admin

router = APIRouter()


@router.get("", response_model=List[TopicConfig])
def get_topic_configs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取主题配置列表
    - 管理员：可以查看所有配置
    - 普通用户：只能查看自己的配置
    """
    user_id = None if current_user.is_admin else current_user.id
    return topic_config_service_module.get_topic_configs(db, skip=skip, limit=limit, user_id=user_id)


@router.get("/{config_id}", response_model=TopicConfig)
def get_topic_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取单个主题配置
    - 管理员：可以查看任何配置
    - 普通用户：只能查看自己的配置
    """
    user_id = None if current_user.is_admin else current_user.id
    config = topic_config_service_module.get_topic_config(db, config_id, user_id=user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Topic Config not found")
    return config


@router.post("", response_model=TopicConfig, status_code=status.HTTP_201_CREATED)
def create_topic_config(
    config: TopicConfigCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建主题配置
    - 管理员：可以创建系统级配置（user_id=None）或用户配置
    - 普通用户：只能为自己创建配置
    """
    try:
        # 普通用户只能为自己创建，管理员可以创建系统级配置（通过不传user_id）
        user_id = current_user.id
        return topic_config_service_module.create_topic_config(db, config, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{config_id}", response_model=TopicConfig)
def update_topic_config(
    config_id: int, 
    config_update: TopicConfigUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新主题配置
    - 管理员：可以更新任何配置
    - 普通用户：只能更新自己的配置
    """
    # 权限检查
    user_id = None if current_user.is_admin else current_user.id
    existing_config = topic_config_service_module.get_topic_config(db, config_id, user_id=user_id)
    if not existing_config:
        raise HTTPException(status_code=404, detail="Topic Config not found")
    
    # 如果更新了激活状态，需要重启MQTT服务
    if config_update.is_active is not None:
        if config_update.is_active:
            success = topic_config_service_module.activate_topic_config(db, config_id)
        else:
            success = topic_config_service_module.deactivate_topic_config(db, config_id)
        if not success:
            raise HTTPException(status_code=404, detail="Topic Config not found")
        
        # 重启MQTT服务以应用新的订阅设置
        from services.mqtt_service import restart_mqtt_service
        restart_mqtt_service()
    
    try:
        config = topic_config_service_module.update_topic_config(db, config_id, config_update)
        if not config:
            raise HTTPException(status_code=404, detail="Topic Config not found")
        return config
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除主题配置
    - 管理员：可以删除任何配置
    - 普通用户：只能删除自己的配置
    """
    # 权限检查
    user_id = None if current_user.is_admin else current_user.id
    existing_config = topic_config_service_module.get_topic_config(db, config_id, user_id=user_id)
    if not existing_config:
        raise HTTPException(status_code=404, detail="Topic Config not found")
    
    success = topic_config_service_module.delete_topic_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic Config not found")
    
    # 重启MQTT服务以更新订阅列表
    from services.mqtt_service import restart_mqtt_service
    restart_mqtt_service()
    
    return None


@router.post("/{config_id}/activate", response_model=TopicConfig)
def activate_topic_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """激活主题配置
    - 管理员：可以激活任何配置
    - 普通用户：只能激活自己的配置
    """
    # 权限检查
    user_id = None if current_user.is_admin else current_user.id
    existing_config = topic_config_service_module.get_topic_config(db, config_id, user_id=user_id)
    if not existing_config:
        raise HTTPException(status_code=404, detail="Topic Config not found")
    
    success = topic_config_service_module.activate_topic_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic Config not found")
    
    # 重启MQTT服务
    from services.mqtt_service import restart_mqtt_service
    restart_mqtt_service()
    
    config = topic_config_service_module.get_topic_config(db, config_id)
    return config