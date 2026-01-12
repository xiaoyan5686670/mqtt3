"""主题配置服务层"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models.topic_config import TopicConfigModel
from schemas.topic_config import TopicConfigCreate, TopicConfigUpdate


def get_topic_config(db: Session, config_id: int) -> Optional[TopicConfigModel]:
    """根据ID获取主题配置"""
    return db.query(TopicConfigModel).filter(TopicConfigModel.id == config_id).first()


def get_topic_configs(db: Session, skip: int = 0, limit: int = 100) -> List[TopicConfigModel]:
    """获取主题配置列表"""
    return db.query(TopicConfigModel).offset(skip).limit(limit).all()


def get_active_topic_configs(db: Session) -> List[TopicConfigModel]:
    """获取所有激活的主题配置"""
    return db.query(TopicConfigModel).filter(TopicConfigModel.is_active == True).all()


def create_topic_config(db: Session, config: TopicConfigCreate) -> TopicConfigModel:
    """创建主题配置"""
    db_config = TopicConfigModel(**config.model_dump())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def update_topic_config(db: Session, config_id: int, config_update: TopicConfigUpdate) -> Optional[TopicConfigModel]:
    """更新主题配置"""
    db_config = db.query(TopicConfigModel).filter(TopicConfigModel.id == config_id).first()
    if not db_config:
        return None
    
    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config


def delete_topic_config(db: Session, config_id: int) -> bool:
    """删除主题配置"""
    db_config = db.query(TopicConfigModel).filter(TopicConfigModel.id == config_id).first()
    if not db_config:
        return False
    
    db.delete(db_config)
    db.commit()
    return True


def activate_topic_config(db: Session, config_id: int) -> bool:
    """激活主题配置"""
    db_config = db.query(TopicConfigModel).filter(TopicConfigModel.id == config_id).first()
    if not db_config:
        return False
    
    db_config.is_active = True
    db.commit()
    return True


def deactivate_topic_config(db: Session, config_id: int) -> bool:
    """停用主题配置"""
    db_config = db.query(TopicConfigModel).filter(TopicConfigModel.id == config_id).first()
    if not db_config:
        return False
    
    db_config.is_active = False
    db.commit()
    return True