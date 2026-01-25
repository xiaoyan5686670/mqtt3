"""MQTT配置服务层"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models.mqtt_config import MQTTConfigModel
from schemas.mqtt_config import MQTTConfigCreate, MQTTConfigUpdate


def get_mqtt_config(db: Session, config_id: int, user_id: Optional[int] = None) -> Optional[MQTTConfigModel]:
    """根据ID获取MQTT配置
    
    Args:
        config_id: 配置ID
        user_id: 可选，验证配置是否属于该用户。如果为None，不进行用户验证
    """
    query = db.query(MQTTConfigModel).filter(MQTTConfigModel.id == config_id)
    
    if user_id is not None:
        query = query.filter(MQTTConfigModel.user_id == user_id)
    
    return query.first()


def get_mqtt_configs(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[MQTTConfigModel]:
    """获取MQTT配置列表
    
    Args:
        skip: 跳过数量
        limit: 限制数量
        user_id: 可选，按用户ID筛选。如果为None，返回所有配置（管理员使用）
    """
    query = db.query(MQTTConfigModel)
    
    if user_id is not None:
        query = query.filter(MQTTConfigModel.user_id == user_id)
    
    return query.offset(skip).limit(limit).all()


def get_active_mqtt_config(db: Session, user_id: Optional[int] = None) -> Optional[MQTTConfigModel]:
    """获取激活的MQTT配置
    
    Args:
        user_id: 可选，按用户ID筛选。如果为None，返回任意激活的配置
    """
    query = db.query(MQTTConfigModel).filter(MQTTConfigModel.is_active == True)
    
    if user_id is not None:
        query = query.filter(MQTTConfigModel.user_id == user_id)
    
    return query.first()


def create_mqtt_config(db: Session, config: MQTTConfigCreate, user_id: Optional[int] = None) -> MQTTConfigModel:
    """创建MQTT配置
    
    Args:
        config: MQTT配置数据
        user_id: 可选，所属用户ID。如果为None，创建系统级配置
    
    Raises:
        ValueError: 如果配置名称在同一用户内已存在
    """
    # 验证同一用户内配置名称唯一性
    existing = db.query(MQTTConfigModel).filter(
        MQTTConfigModel.name == config.name,
        MQTTConfigModel.user_id == user_id
    ).first()
    
    if existing:
        if user_id is None:
            raise ValueError(f"系统级配置名称 '{config.name}' 已存在")
        else:
            raise ValueError(f"配置名称 '{config.name}' 已存在，请使用其他名称")
    
    config_data = config.model_dump()
    if user_id is not None:
        config_data["user_id"] = user_id
    
    db_config = MQTTConfigModel(**config_data)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def update_mqtt_config(db: Session, config_id: int, config_update: MQTTConfigUpdate) -> Optional[MQTTConfigModel]:
    """更新MQTT配置
    
    Raises:
        ValueError: 如果配置名称在同一用户内已存在（排除当前配置）
    """
    db_config = db.query(MQTTConfigModel).filter(MQTTConfigModel.id == config_id).first()
    if not db_config:
        return None
    
    update_data = config_update.model_dump(exclude_unset=True)
    
    # 如果更新了名称，检查同一用户内是否已存在同名配置（排除当前配置）
    if "name" in update_data and update_data["name"] != db_config.name:
        existing = db.query(MQTTConfigModel).filter(
            MQTTConfigModel.name == update_data["name"],
            MQTTConfigModel.user_id == db_config.user_id,
            MQTTConfigModel.id != config_id
        ).first()
        
        if existing:
            if db_config.user_id is None:
                raise ValueError(f"系统级配置名称 '{update_data['name']}' 已存在")
            else:
                raise ValueError(f"配置名称 '{update_data['name']}' 已存在，请使用其他名称")
    
    for key, value in update_data.items():
        setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config


def delete_mqtt_config(db: Session, config_id: int) -> bool:
    """删除MQTT配置"""
    db_config = db.query(MQTTConfigModel).filter(MQTTConfigModel.id == config_id).first()
    if not db_config:
        return False
    
    db.delete(db_config)
    db.commit()
    return True


def activate_mqtt_config(db: Session, config_id: int) -> bool:
    """激活MQTT配置（不影响其他配置）"""
    # 只激活指定配置，不影响其他配置
    db_config = db.query(MQTTConfigModel).filter(MQTTConfigModel.id == config_id).first()
    if not db_config:
        return False
    
    db_config.is_active = True
    db.commit()
    return True


def deactivate_mqtt_config(db: Session, config_id: int) -> bool:
    """停用MQTT配置"""
    db_config = db.query(MQTTConfigModel).filter(MQTTConfigModel.id == config_id).first()
    if not db_config:
        return False
    
    db_config.is_active = False
    db.commit()
    return True