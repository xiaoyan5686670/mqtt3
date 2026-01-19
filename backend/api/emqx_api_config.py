"""EMQX API 配置管理"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import requests
from typing import Optional

from core.database import get_db
from schemas.user import User
from api.auth import require_admin
from models.mqtt_config import MQTTConfigModel
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


class EmqxApiConfigRequest(BaseModel):
    """EMQX API 配置请求模型"""
    api_port: int = 18083
    api_key: str
    api_secret: str


class EmqxApiConfigResponse(BaseModel):
    """EMQX API 配置响应模型"""
    api_port: int
    api_key: str
    api_secret: str


@router.get("")
async def get_emqx_api_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取 EMQX API 配置（仅管理员）"""
    try:
        # 获取激活的 MQTT 配置
        mqtt_config = db.query(MQTTConfigModel).filter(
            MQTTConfigModel.is_active == True
        ).first()
        
        if not mqtt_config:
            raise HTTPException(
                status_code=404,
                detail="未找到激活的 MQTT 配置"
            )
        
        return {
            "api_port": mqtt_config.api_port or 18083,
            "api_key": mqtt_config.api_key or "",
            "api_secret": mqtt_config.api_secret or ""
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取 EMQX API 配置失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取配置失败: {str(e)}"
        )


@router.post("")
async def save_emqx_api_config(
    request: EmqxApiConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """保存 EMQX API 配置（仅管理员）"""
    try:
        # 获取激活的 MQTT 配置
        mqtt_config = db.query(MQTTConfigModel).filter(
            MQTTConfigModel.is_active == True
        ).first()
        
        if not mqtt_config:
            raise HTTPException(
                status_code=404,
                detail="未找到激活的 MQTT 配置，请先在 MQTT 配置管理中激活一个配置"
            )
        
        # 更新 EMQX API 配置
        mqtt_config.api_port = request.api_port
        mqtt_config.api_key = request.api_key
        mqtt_config.api_secret = request.api_secret
        
        db.commit()
        db.refresh(mqtt_config)
        
        logger.info(f"EMQX API 配置已更新: {mqtt_config.name}")
        
        return {
            "success": True,
            "message": "EMQX API 配置保存成功",
            "config": {
                "api_port": mqtt_config.api_port,
                "api_key": mqtt_config.api_key,
                "api_secret": mqtt_config.api_secret
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存 EMQX API 配置失败: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"保存配置失败: {str(e)}"
        )


@router.post("/test")
async def test_emqx_api_connection(
    request: EmqxApiConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """测试 EMQX API 连接（仅管理员）"""
    try:
        # 获取激活的 MQTT 配置以获取服务器地址
        mqtt_config = db.query(MQTTConfigModel).filter(
            MQTTConfigModel.is_active == True
        ).first()
        
        if not mqtt_config:
            raise HTTPException(
                status_code=404,
                detail="未找到激活的 MQTT 配置"
            )
        
        # 构建 EMQX API URL
        api_url = f"http://{mqtt_config.server}:{request.api_port}/api/v5/clients"
        
        logger.info(f"测试 EMQX API 连接: {api_url}")
        
        # 使用 API Key 和 Secret Key 进行认证
        response = requests.get(
            api_url,
            auth=(request.api_key, request.api_secret),
            timeout=10,
            params={'limit': 10}
        )
        
        if response.status_code == 200:
            data = response.json()
            client_count = data.get('meta', {}).get('count', 0)
            
            logger.info(f"EMQX API 连接成功，当前客户端数: {client_count}")
            
            return {
                "success": True,
                "message": f"连接成功！当前有 {client_count} 个客户端在线",
                "client_count": client_count,
                "api_url": api_url
            }
        elif response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="认证失败：API Key 或 Secret Key 不正确"
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"EMQX API 返回错误: {response.text}"
            )
            
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=408,
            detail="连接超时：请检查 EMQX 服务器地址和端口是否正确"
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="连接失败：无法连接到 EMQX 服务器，请检查服务器是否运行"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试 EMQX API 连接失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"测试连接失败: {str(e)}"
        )
