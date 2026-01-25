"""主题配置服务层"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models.topic_config import TopicConfigModel
from schemas.topic_config import TopicConfigCreate, TopicConfigUpdate


def get_topic_config(db: Session, config_id: int, user_id: Optional[int] = None) -> Optional[TopicConfigModel]:
    """根据ID获取主题配置
    
    Args:
        config_id: 配置ID
        user_id: 可选，验证配置是否属于该用户。如果为None，不进行用户验证
    """
    query = db.query(TopicConfigModel).filter(TopicConfigModel.id == config_id)
    
    if user_id is not None:
        query = query.filter(TopicConfigModel.user_id == user_id)
    
    return query.first()


def get_topic_configs(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[TopicConfigModel]:
    """获取主题配置列表
    
    Args:
        skip: 跳过数量
        limit: 限制数量
        user_id: 可选，按用户ID筛选。如果为None，返回所有配置（管理员使用）
    """
    query = db.query(TopicConfigModel)
    
    if user_id is not None:
        query = query.filter(TopicConfigModel.user_id == user_id)
    
    return query.offset(skip).limit(limit).all()


def get_active_topic_configs(db: Session, user_id: Optional[int] = None) -> List[TopicConfigModel]:
    """获取所有激活的主题配置
    
    Args:
        user_id: 可选，按用户ID筛选。如果为None，返回所有激活的配置
    """
    query = db.query(TopicConfigModel).filter(TopicConfigModel.is_active == True)
    
    if user_id is not None:
        query = query.filter(TopicConfigModel.user_id == user_id)
    
    return query.all()


def create_topic_config(db: Session, config: TopicConfigCreate, user_id: Optional[int] = None) -> TopicConfigModel:
    """创建主题配置
    
    Args:
        config: 主题配置数据
        user_id: 可选，所属用户ID。如果为None，创建系统级配置
    
    Raises:
        ValueError: 如果配置名称在同一用户内已存在
    """
    # 验证同一用户内配置名称唯一性
    existing = db.query(TopicConfigModel).filter(
        TopicConfigModel.name == config.name,
        TopicConfigModel.user_id == user_id
    ).first()
    
    if existing:
        if user_id is None:
            raise ValueError(f"系统级主题配置名称 '{config.name}' 已存在")
        else:
            raise ValueError(f"主题配置名称 '{config.name}' 已存在，请使用其他名称")
    
    config_data = config.model_dump()
    if user_id is not None:
        config_data["user_id"] = user_id
    
    db_config = TopicConfigModel(**config_data)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def update_topic_config(db: Session, config_id: int, config_update: TopicConfigUpdate) -> Optional[TopicConfigModel]:
    """更新主题配置
    
    Raises:
        ValueError: 如果配置名称在同一用户内已存在（排除当前配置）
    """
    db_config = db.query(TopicConfigModel).filter(TopicConfigModel.id == config_id).first()
    if not db_config:
        return None
    
    update_data = config_update.model_dump(exclude_unset=True)
    
    # 如果更新了名称，检查同一用户内是否已存在同名配置（排除当前配置）
    if "name" in update_data and update_data["name"] != db_config.name:
        existing = db.query(TopicConfigModel).filter(
            TopicConfigModel.name == update_data["name"],
            TopicConfigModel.user_id == db_config.user_id,
            TopicConfigModel.id != config_id
        ).first()
        
        if existing:
            if db_config.user_id is None:
                raise ValueError(f"系统级主题配置名称 '{update_data['name']}' 已存在")
            else:
                raise ValueError(f"主题配置名称 '{update_data['name']}' 已存在，请使用其他名称")
    
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


def find_topic_config_by_device_name(db: Session, device_name: str) -> Optional[TopicConfigModel]:
    """根据设备名称自动匹配 TopicConfig
    
    匹配策略：
    1. 将设备名转换为可能的主题格式（如 stm32_3 -> stm32/3）
    2. 查找所有激活的 TopicConfig，检查其 subscribe_topics 是否包含该主题
    3. 如果找到匹配的 TopicConfig，返回它
    
    Args:
        db: 数据库会话
        device_name: 设备名称（如 "stm32_3" 或 "stm32/3"）
    
    Returns:
        匹配的 TopicConfig，如果没找到则返回 None
    """
    if not device_name:
        return None
    
    import json
    import re
    
    # 生成可能的主题格式
    possible_topics = []
    name = device_name.strip()
    
    # 如果设备名本身就是主题格式（如 "stm32/3"），直接使用
    if "/" in name:
        possible_topics.append(name)
        # 也尝试下划线版本
        possible_topics.append(name.replace("/", "_"))
    
    # 如果设备名包含下划线或横线，转换为斜杠格式
    if "_" in name or "-" in name:
        # 如 stm32_3 -> stm32/3
        topic_with_slash = re.sub(r"[_-]", "/", name)
        possible_topics.append(topic_with_slash)
        # 也保留原始格式
        possible_topics.append(name)
    
    # 去重
    possible_topics = list(set(possible_topics))
    
    # 获取所有激活的 TopicConfig（不限制用户，用于设备匹配）
    active_configs = get_active_topic_configs(db, user_id=None)
    
    # 解析每个 TopicConfig 的 subscribe_topics，查找匹配
    for config in active_configs:
        if not config.subscribe_topics:
            continue
        
        # 解析 subscribe_topics
        topics_list = []
        try:
            # 尝试解析为 JSON 数组
            parsed = json.loads(config.subscribe_topics)
            if isinstance(parsed, list):
                topics_list = [str(t).strip() for t in parsed if t]
        except (json.JSONDecodeError, TypeError):
            # 如果不是 JSON 格式，按换行符或逗号分割
            if '\n' in config.subscribe_topics:
                topics_list = [t.strip() for t in config.subscribe_topics.split('\n') if t.strip()]
            else:
                topics_list = [t.strip() for t in config.subscribe_topics.split(',') if t.strip()]
        
        # 检查是否有匹配的主题
        for topic in topics_list:
            # 精确匹配
            if topic in possible_topics:
                return config
            # 部分匹配（如 subscribe_topics 是 "stm32/3"，设备名是 "stm32_3"）
            topic_normalized = topic.replace("/", "_").replace("-", "_")
            for possible_topic in possible_topics:
                possible_normalized = possible_topic.replace("/", "_").replace("-", "_")
                if topic_normalized == possible_normalized:
                    return config
    
    return None