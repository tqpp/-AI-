from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import os
from datetime import datetime, date
import json

from ..dependencies import get_db
from ..models import DetectionStatus
from ..services.detection import DetectionService
from .base import CamelModel

router = APIRouter(
    prefix="/api/detections",
    tags=["detections"],
)

# ----- API模型定义 -----
class DetectionCreate(CamelModel):
    text: Optional[str] = None
    confidence: Optional[float] = None
    status: Optional[str] = None
    device_id: Optional[int] = None
    image_data: Optional[str] = None
    processed_image_data: Optional[str] = None
    operation_id: Optional[int] = None
    operation_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DetectionResponse(CamelModel):
    id: int
    text: Optional[str] = None
    confidence: Optional[float] = None
    status: str
    device_id: Optional[int] = None
    device_name: Optional[str] = None
    timestamp: datetime
    image_path: Optional[str] = None
    processed_image_path: Optional[str] = None
    operation_id: Optional[int] = None
    operation_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class PaginatedDetectionResponse(CamelModel):
    items: List[DetectionResponse]
    total: int
    page: int
    per_page: int
    pages: int

# ----- 路由处理函数 -----
@router.post("", response_model=DetectionResponse)
async def create_detection(
    detection: DetectionCreate,
    db: Session = Depends(get_db)
):
    """创建新的检测记录"""
    detection_service = DetectionService(db)
    
    # 转换状态字符串为枚举值
    status = DetectionStatus.UNKNOWN
    if detection.status:
        status_map = {
            "pass": DetectionStatus.PASS,
            "合格": DetectionStatus.PASS,
            "fail": DetectionStatus.FAIL,
            "不合格": DetectionStatus.FAIL
        }
        if detection.status.lower() in status_map:
            status = status_map[detection.status.lower()]
        else:
            try:
                status = DetectionStatus(detection.status)
            except ValueError:
                pass
    
    # 创建检测记录
    result = detection_service.create_detection(
        text=detection.text,
        confidence=detection.confidence,
        status=status,
        device_id=detection.device_id,
        image_data=detection.image_data,
        processed_image_data=detection.processed_image_data,
        operation_id=detection.operation_id,
        operation_type=detection.operation_type,
        metadata=detection.metadata
    )
    
    # 转换为响应模型
    result.metadata = result.detection_metadata
    return DetectionResponse.model_validate(result)

@router.get("", response_model=PaginatedDetectionResponse)
async def list_detections(
    page: int = Query(1, gt=0),
    per_page: int = Query(10, gt=0, le=100),
    search_text: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    device_id: Optional[int] = None,
    confidence_min: Optional[float] = None,
    confidence_max: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """获取检测记录列表，带分页和过滤"""
    detection_service = DetectionService(db)
    
    # 记录日期参数，用于调试
    print(f"接收到的日期范围参数: date_from={date_from}, date_to={date_to}")
    
    # 转换日期字符串为日期对象
    date_from_obj = None
    date_to_obj = None
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            print(f"解析后的起始日期: {date_from_obj}")
        except ValueError as e:
            print(f"无法解析起始日期 '{date_from}': {str(e)}")
            raise HTTPException(status_code=400, detail=f"无效的起始日期格式: {date_from}，应为YYYY-MM-DD")
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            print(f"解析后的结束日期: {date_to_obj}")
        except ValueError as e:
            print(f"无法解析结束日期 '{date_to}': {str(e)}")
            raise HTTPException(status_code=400, detail=f"无效的结束日期格式: {date_to}，应为YYYY-MM-DD")
    
    # 转换日期对象为日期时间对象
    date_from_dt = datetime.combine(date_from_obj, datetime.min.time()) if date_from_obj else None
    date_to_dt = datetime.combine(date_to_obj, datetime.min.time()) if date_to_obj else None
    
    # 获取检测记录
    result = detection_service.list_detections(
        page=page,
        per_page=per_page,
        search_text=search_text,
        status=status,
        date_from=date_from_dt,
        date_to=date_to_dt,
        device_id=device_id,
        confidence_min=confidence_min,
        confidence_max=confidence_max
    )
    
    # 获取设备名称
    for detection in result["items"]:
        if detection.device:
            setattr(detection, "device_name", detection.device.name)
        else:
            setattr(detection, "device_name", None)
            
        # 将路径转换为URL
        if detection.image_path:
            detection.image_path = f"/uploads/detections/{os.path.basename(detection.image_path)}"
        if detection.processed_image_path:
            detection.processed_image_path = f"/uploads/detections/{os.path.basename(detection.processed_image_path)}"
        
        # 添加metadata字段映射
        detection.metadata = detection.detection_metadata
    
    # 转换为响应模型
    return PaginatedDetectionResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        pages=result["pages"]
    )

@router.get("/{detection_id}", response_model=DetectionResponse)
async def get_detection(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """获取单个检测记录详情"""
    detection_service = DetectionService(db)
    detection = detection_service.get_detection(detection_id)
    
    if not detection:
        raise HTTPException(status_code=404, detail="检测记录不存在")
    
    # 获取设备名称
    if detection.device:
        setattr(detection, "device_name", detection.device.name)
    else:
        setattr(detection, "device_name", None)
        
    # 将路径转换为URL
    if detection.image_path:
        detection.image_path = f"/uploads/detections/{os.path.basename(detection.image_path)}"
    if detection.processed_image_path:
        detection.processed_image_path = f"/uploads/detections/{os.path.basename(detection.processed_image_path)}"
    
    # 添加metadata字段映射
    detection.metadata = detection.detection_metadata
    
    return DetectionResponse.model_validate(detection)

@router.delete("/{detection_id}")
async def delete_detection(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """删除检测记录"""
    detection_service = DetectionService(db)
    success = detection_service.delete_detection(detection_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="检测记录不存在")
    
    return {"message": "检测记录已删除"}

@router.delete("")
async def clear_detections(
    before_date: Optional[str] = None,
    status: Optional[str] = None,
    device_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """清除满足条件的检测记录"""
    detection_service = DetectionService(db)
    
    # 转换日期字符串为日期对象
    before_date_obj = None
    if before_date:
        try:
            before_date_obj = datetime.strptime(before_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的日期格式: {before_date}，应为YYYY-MM-DD")
    
    # 转换日期对象为日期时间对象
    before_date_dt = datetime.combine(before_date_obj, datetime.min.time()) if before_date_obj else None
    
    # 转换状态字符串为枚举值
    status_enum = None
    if status:
        status_map = {
            "pass": DetectionStatus.PASS,
            "合格": DetectionStatus.PASS,
            "fail": DetectionStatus.FAIL,
            "不合格": DetectionStatus.FAIL,
            "unknown": DetectionStatus.UNKNOWN,
            "未知": DetectionStatus.UNKNOWN
        }
        if status.lower() in status_map:
            status_enum = status_map[status.lower()]
        else:
            try:
                status_enum = DetectionStatus(status)
            except ValueError:
                pass
    
    # 清除记录
    count = detection_service.clear_detections(
        before_date=before_date_dt,
        status=status_enum,
        device_id=device_id
    )
    
    return {"message": f"已清除 {count} 条检测记录"} 