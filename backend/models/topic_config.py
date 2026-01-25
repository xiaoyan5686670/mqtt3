"""主题配置模型"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class TopicConfigModel(Base):
    """主题配置数据模型"""
    __tablename__ = "topic_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # 移除全局unique，改为用户内唯一
    subscribe_topics = Column(String, nullable=False)  # JSON格式或逗号分隔
    publish_topic = Column(String, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    mqtt_config_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 所属用户ID，NULL表示系统级配置
    json_parse_config = Column(String, nullable=True)  # JSON格式的解析配置
    relay_on_payload = Column(String, nullable=True)  # 继电器开启的payload格式
    relay_off_payload = Column(String, nullable=True)  # 继电器关闭的payload格式
    
    # 关系
    user = relationship("UserModel", back_populates="topic_configs")