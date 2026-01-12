"""MQTT消息发布API"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services.mqtt_service import get_mqtt_service
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


class MQTTPublishRequest(BaseModel):
    """MQTT发布请求模型"""
    topic: str
    message: str = ""
    qos: int = 0


@router.post("/publish")
async def publish_message(request: MQTTPublishRequest, db: Session = Depends(get_db)):
    """发布消息到MQTT主题"""
    try:
        mqtt_service = get_mqtt_service()
        success = mqtt_service.publish_message(request.topic, request.message, request.qos)
        
        if success:
            return {
                "success": True,
                "message": f"消息已成功发布到主题 {request.topic}",
                "topic": request.topic,
                "payload": request.message
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="发布消息失败，请检查MQTT连接状态"
            )
    except Exception as e:
        logger.error(f"发布消息API错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"发布消息时出错: {str(e)}"
        )
