"""MQTT配置模型"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class MQTTConfigModel(Base):
    """MQTT配置数据模型"""
    __tablename__ = "mqtt_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # 移除全局unique，改为用户内唯一
    server = Column(String, nullable=False)
    port = Column(Integer, nullable=False, default=1883)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 所属用户ID，NULL表示系统级配置
    
    # EMQX API 配置字段
    api_port = Column(Integer, default=18083, nullable=True)
    api_key = Column(String, nullable=True)
    api_secret = Column(String, nullable=True)
    
    # 关系
    user = relationship("UserModel", back_populates="mqtt_configs")