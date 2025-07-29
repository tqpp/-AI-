from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..dependencies import get_db
from ..services.dashboard import DashboardService, get_dashboard_service
from ..models import AlertType

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/system-status")
def get_system_status(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """获取系统状态信息"""
    return dashboard_service.get_system_status()

@router.get("/detection-stats")
def get_detection_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """获取今日检测统计"""
    return dashboard_service.get_detection_stats()

@router.get("/defect-stats")
def get_defect_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """获取缺陷统计"""
    return dashboard_service.get_defect_stats()

@router.get("/accuracy")
def get_accuracy(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """获取检测准确率统计"""
    return dashboard_service.get_accuracy()

@router.get("/alerts")
def get_recent_alerts(
    limit: int = Query(10, description="返回告警的数量限制"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """获取最近告警"""
    return dashboard_service.get_recent_alerts(limit=limit)

@router.post("/alerts")
def create_alert(
    message: str,
    alert_type: str = "INFO",
    device_id: Optional[int] = None,
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """创建新的告警"""
    # 将字符串类型转换为枚举类型
    try:
        alert_type_enum = AlertType[alert_type]
    except KeyError:
        alert_type_enum = AlertType.INFO
    
    alert = dashboard_service.create_alert(
        message=message,
        alert_type=alert_type_enum,
        device_id=device_id
    )
    
    if not alert:
        raise HTTPException(status_code=500, detail="创建告警失败")
    
    return {"id": str(alert.id), "message": "告警创建成功"}

@router.put("/alerts/{alert_id}/read")
def mark_alert_as_read(
    alert_id: int = Path(..., description="告警ID"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """将告警标记为已读"""
    success = dashboard_service.mark_alert_as_read(alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="告警不存在或更新失败")
    
    return {"message": "已将告警标记为已读"}

@router.get("/device-status")
def get_device_status_summary(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """获取设备状态摘要"""
    return dashboard_service.get_device_status_summary()

@router.get("/detection-trends")
def get_daily_detection_trends(
    days: int = Query(7, description="要获取的天数", ge=1, le=30),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """获取每日检测趋势"""
    return dashboard_service.get_daily_detection_trends(days=days) 