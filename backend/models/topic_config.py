"""主题配置模型"""
from sqlalchemy import Column, Integer, String, Boolean
from core.database import Base


class TopicConfigModel(Base):
    """主题配置数据模型"""
    __tablename__ = "topic_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    subscribe_topics = Column(String, nullable=False)  # JSON格式或逗号分隔
    publish_topic = Column(String, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    mqtt_config_id = Column(Integer, nullable=True)
    json_parse_config = Column(String, nullable=True)  # JSON格式的解析配置