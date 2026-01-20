"""传感器数据相关的API路由"""
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.sensor import SensorData, SensorDataUpdate
from schemas.user import User
from services import sensor_service as sensor_service_module
from api.auth import get_current_active_user, require_admin

router = APIRouter()


@router.get("/device/{device_id}", response_model=List[SensorData])
def get_device_sensors(
    device_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取设备的所有传感器数据（需要认证）"""
    sensors = sensor_service_module.get_device_sensors(db, device_id)
    return sensors


@router.get("/device/{device_id}/latest", response_model=List[SensorData])
def get_latest_device_sensors(
    device_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取设备的最新传感器数据（按类型分组，需要认证）"""
    sensors = sensor_service_module.get_latest_device_sensors(db, device_id)
    return sensors


@router.get("/device/{device_id}/history", response_model=List[SensorData])
def get_device_sensor_history(
    device_id: int,
    sensor_type: Optional[str] = Query(
        None,
        description="传感器类型（如 Temperature1、Humidity1 等），为空则返回所有类型"
    ),
    start_time: Optional[str] = Query(
        None,
        description="开始时间（ISO 格式，例如 2026-01-14T00:00:00）"
    ),
    end_time: Optional[str] = Query(
        None,
        description="结束时间（ISO 格式），不传则默认为当前时间"
    ),
    time_range: Optional[str] = Query(
        None,
        description="时间范围：day / week / month，提供该参数时会自动计算时间范围"
    ),
    limit: Optional[int] = Query(
        None,
        description="最多返回的数据点数量"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取设备的历史传感器数据（按时间范围）

    优先使用 time_range（day/week/month）自动计算时间范围；
    如果未提供 time_range，则使用 start_time / end_time。
    """
    # 计算时间范围
    if time_range:
        now = datetime.utcnow()
        if time_range == "day":
            # 今天的数据：从今天00:00:00到现在
            start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = now
        elif time_range == "week":
            # 最近7天的数据
            start_dt = now - timedelta(weeks=1)
            end_dt = now
        elif time_range == "month":
            # 最近30天的数据
            start_dt = now - timedelta(days=30)
            end_dt = now
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid time_range. Use 'day', 'week', or 'month'."
            )
    else:
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None

    sensors = sensor_service_module.get_device_sensors_by_time_range(
        db=db,
        device_id=device_id,
        sensor_type=sensor_type,
        start_time=start_dt,
        end_time=end_dt,
        limit=limit,
    )
    return sensors


@router.get("/latest", response_model=List[SensorData])
def get_latest_sensors(
    limit: int = 50, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取最新的传感器数据（需要认证）"""
    sensors = sensor_service_module.get_latest_sensors(db, limit=limit)
    return sensors


@router.put("/{sensor_id}/display-name", response_model=SensorData)
def update_sensor_display_name(
    sensor_id: int, 
    update_data: SensorDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新传感器的显示名称（仅管理员）"""
    sensor = sensor_service_module.update_sensor_display_name(
        db, sensor_id, update_data.display_name
    )
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.put("/device/{device_id}/type/{sensor_type}/display-name", response_model=SensorData)
def update_sensor_display_name_by_type(
    device_id: int,
    sensor_type: str,
    update_data: SensorDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """根据设备ID和传感器类型更新显示名称（仅管理员）"""
    sensor = sensor_service_module.update_sensor_by_type_and_device(
        db, device_id, sensor_type, update_data.display_name
    )
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor