"""API路由模块"""
from fastapi import APIRouter
from . import devices, mqtt_configs, topic_configs, sensors, mqtt_publish, auth, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
api_router.include_router(mqtt_configs.router, prefix="/mqtt-configs", tags=["mqtt-configs"])
api_router.include_router(topic_configs.router, prefix="/topic-configs", tags=["topic-configs"])
api_router.include_router(mqtt_publish.router, prefix="/mqtt", tags=["mqtt"])