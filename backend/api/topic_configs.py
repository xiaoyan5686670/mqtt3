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
    current_user: User = Depends(require_admin)
):
    """获取主题配置列表（仅管理员）"""
    return topic_config_service_module.get_topic_configs(db, skip=skip, limit=limit)


@router.get("/{config_id}", response_model=TopicConfig)
def get_topic_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取单个主题配置（仅管理员）"""
    config = topic_config_service_module.get_topic_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Topic Config not found")
    return config


@router.post("", response_model=TopicConfig, status_code=status.HTTP_201_CREATED)
def create_topic_config(
    config: TopicConfigCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """创建主题配置（仅管理员）"""
    return topic_config_service_module.create_topic_config(db, config)


@router.put("/{config_id}", response_model=TopicConfig)
def update_topic_config(
    config_id: int, 
    config_update: TopicConfigUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新主题配置（仅管理员）"""
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
    
    config = topic_config_service_module.update_topic_config(db, config_id, config_update)
    if not config:
        raise HTTPException(status_code=404, detail="Topic Config not found")
    return config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic_config(
    config_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除主题配置（仅管理员）"""
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
    current_user: User = Depends(require_admin)
):
    """激活主题配置（仅管理员）"""
    success = topic_config_service_module.activate_topic_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic Config not found")
    
    # 重启MQTT服务
    from services.mqtt_service import restart_mqtt_service
    restart_mqtt_service()
    
    config = topic_config_service_module.get_topic_config(db, config_id)
    return config