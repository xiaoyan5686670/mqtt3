"""MQTT配置服务层"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models.mqtt_config import MQTTConfigModel
from schemas.mqtt_config import MQTTConfigCreate, MQTTConfigUpdate


def get_mqtt_config(db: Session, config_id: int) -> Optional[MQTTConfigModel]:
    """根据ID获取MQTT配置"""
    return db.query(MQTTConfigModel).filter(MQTTConfigModel.id == config_id).first()


def get_mqtt_configs(db: Session, skip: int = 0, limit: int = 100) -> List[MQTTConfigModel]:
    """获取MQTT配置列表"""
    return db.query(MQTTConfigModel).offset(skip).limit(limit).all()


def get_active_mqtt_config(db: Session) -> Optional[MQTTConfigModel]:
    """获取激活的MQTT配置"""
    return db.query(MQTTConfigModel).filter(MQTTConfigModel.is_active == True).first()


def create_mqtt_config(db: Session, config: MQTTConfigCreate) -> MQTTConfigModel:
    """创建MQTT配置"""
    db_config = MQTTConfigModel(**config.model_dump())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def update_mqtt_config(db: Session, config_id: int, config_update: MQTTConfigUpdate) -> Optional[MQTTConfigModel]:
    """更新MQTT配置"""
    db_config = db.query(MQTTConfigModel).filter(MQTTConfigModel.id == config_id).first()
    if not db_config:
        return None
    
    update_data = config_update.model_dump(exclude_unset=True)
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
    """激活MQTT配置（同时停用其他配置）"""
    # 先将所有配置设为非激活
    db.query(MQTTConfigModel).update({MQTTConfigModel.is_active: False})
    
    # 激活指定配置
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