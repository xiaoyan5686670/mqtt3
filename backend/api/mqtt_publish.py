"""MQTT消息发布API"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import requests

from core.database import get_db
from schemas.user import User
from services.mqtt_service import get_mqtt_service
from core.logging_config import get_logger
from api.auth import get_current_active_user, require_admin

logger = get_logger(__name__)

router = APIRouter()


class MQTTPublishRequest(BaseModel):
    """MQTT发布请求模型"""
    topic: str
    message: str = ""
    qos: int = 0


@router.post("/publish")
async def publish_message(
    request: MQTTPublishRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """发布消息到MQTT主题
    - 管理员：可以使用全局MQTT服务发布
    - 普通用户：只能使用自己的MQTT服务发布
    """
    try:
        # 如果是管理员，使用全局服务
        if current_user.is_admin:
            mqtt_service = get_mqtt_service()
            success = mqtt_service.publish_message(request.topic, request.message, request.qos)
        else:
            # 普通用户：使用自己的MQTT服务
            from services.mqtt_service import get_mqtt_service_manager
            manager = get_mqtt_service_manager()
            user_service = manager.get_user_service(current_user.id)
            
            if not user_service:
                # 如果用户服务不存在，尝试创建并启动
                manager.start_user_service(current_user.id)
                user_service = manager.get_user_service(current_user.id)
            
            if not user_service:
                raise HTTPException(
                    status_code=400,
                    detail="无法初始化MQTT服务，请检查MQTT配置和主题配置"
                )
            
            success = user_service.publish_message(request.topic, request.message, request.qos)
        
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发布消息API错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"发布消息时出错: {str(e)}"
        )


@router.get("/clients")
async def get_mqtt_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取EMQX客户端连接状态列表
    - 管理员：可以查看所有客户端
    - 普通用户：可以查看所有客户端（用于判断自己设备的在线状态）
    注意：设备客户端ID由设备自己设置，无法从客户端ID判断归属，
    所以普通用户也需要获取所有客户端列表，前端会根据设备的clientid来匹配
    """
    try:
        from models.mqtt_config import MQTTConfigModel
        
        # 优先使用用户自己的激活MQTT配置
        # 如果没有，则使用系统级的激活MQTT配置（user_id为None）
        mqtt_config = None
        
        if not current_user.is_admin:
            # 普通用户：先查找自己的激活配置
            user_config = db.query(MQTTConfigModel).filter(
                MQTTConfigModel.is_active == True,
                MQTTConfigModel.user_id == current_user.id
            ).first()
            
            if user_config:
                mqtt_config = user_config
            else:
                # 如果没有自己的配置，使用系统级配置
                system_config = db.query(MQTTConfigModel).filter(
                    MQTTConfigModel.is_active == True,
                    MQTTConfigModel.user_id.is_(None)
                ).first()
                mqtt_config = system_config
        else:
            # 管理员：使用任意激活的配置
            mqtt_config = db.query(MQTTConfigModel).filter(
                MQTTConfigModel.is_active == True
            ).first()
        
        if not mqtt_config:
            logger.warning("未找到激活的MQTT配置")
            return {"data": [], "meta": {"count": 0}}
        
        # 检查是否配置了 API Key
        api_key = mqtt_config.api_key
        api_secret = mqtt_config.api_secret
        
        if not api_key or not api_secret:
            logger.warning("未配置 EMQX API Key，请在系统中配置 API 密钥")
            return {"data": [], "meta": {"count": 0}}
        
        # 构建EMQX API URL
        import requests
        api_port = mqtt_config.api_port or 18083
        api_url = f"http://{mqtt_config.server}:{api_port}/api/v5/clients"
        
        logger.info(f"正在调用 EMQX API: {api_url} (用户: {current_user.username})")
        
        # 使用 API Key 和 Secret Key 进行认证
        response = requests.get(
            api_url,
            auth=(api_key, api_secret),
            timeout=10,
            params={'limit': 1000}  # EMQX API 限制最大 1000
        )
        
        if response.status_code == 200:
            data = response.json()
            client_count = len(data.get('data', []))
            logger.info(f"✅ 成功获取 EMQX 客户端列表，共 {client_count} 个客户端")
            return data
        elif response.status_code == 401:
            logger.error("❌ EMQX API 认证失败，请检查 API Key 和 Secret Key 是否正确")
            return {"data": [], "meta": {"count": 0}}
        else:
            logger.error(f"❌ 获取 EMQX 客户端列表失败，状态码: {response.status_code}, 响应: {response.text}")
            return {"data": [], "meta": {"count": 0}}
            
    except requests.exceptions.Timeout:
        logger.error("❌ EMQX API 请求超时")
        return {"data": [], "meta": {"count": 0}}
    except requests.exceptions.ConnectionError:
        logger.error("❌ 无法连接到 EMQX API，请检查服务器地址和端口")
        return {"data": [], "meta": {"count": 0}}
    except Exception as e:
        logger.error(f"获取MQTT客户端列表API错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取客户端列表时出错: {str(e)}"
        )
