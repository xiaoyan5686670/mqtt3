"""主题配置相关的Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional


class TopicConfigBase(BaseModel):
    name: str
    subscribe_topics: str
    publish_topic: Optional[str] = None
    json_parse_config: Optional[str] = None


class TopicConfigCreate(TopicConfigBase):
    mqtt_config_id: Optional[int] = None


class TopicConfigUpdate(BaseModel):
    name: Optional[str] = None
    subscribe_topics: Optional[str] = None
    publish_topic: Optional[str] = None
    mqtt_config_id: Optional[int] = None
    is_active: Optional[bool] = None
    json_parse_config: Optional[str] = None


class TopicConfig(TopicConfigBase):
    id: int
    is_active: bool = False
    mqtt_config_id: Optional[int] = None
    json_parse_config: Optional[str] = None

    class Config:
        from_attributes = True