from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from fastapi import HTTPException
import os
import base64
import uuid

from ..models import Detection, DetectionStatus, Device
from ..dependencies import get_db
import logging

logger = logging.getLogger(__name__)

class DetectionService:
    def __init__(self, db: Session):
        self.db = db
        
    def create_detection(self, 
                         text: Optional[str] = None,
                         confidence: Optional[float] = None,
                         status: DetectionStatus = DetectionStatus.UNKNOWN,
                         device_id: Optional[int] = None,
                         image_data: Optional[str] = None,
                         processed_image_data: Optional[str] = None,
                         operation_id: Optional[int] = None,
                         operation_type: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Detection:
        """创建新的检测记录"""
        # 处理图像数据 - 保存base64图像到文件
        image_path = None
        processed_image_path = None
        
        if image_data:
            image_path = self._save_image(image_data)
            
        if processed_image_data:
            processed_image_path = self._save_image(processed_image_data)
        
        # 创建新记录
        detection = Detection(
            text=text,
            confidence=confidence,
            status=status,
            device_id=device_id,
            image_path=image_path,
            processed_image_path=processed_image_path,
            operation_id=operation_id,
            operation_type=operation_type,
            timestamp=datetime.now(),
            detection_metadata=metadata or {}
        )
        
        self.db.add(detection)
        self.db.commit()
        self.db.refresh(detection)
        
        return detection
    
    def _save_image(self, image_data: str) -> str:
        """保存base64编码的图像到文件"""
        try:
            # 确保目录存在
            upload_dir = "uploads/detections"
            os.makedirs(upload_dir, exist_ok=True)
            
            # 分析base64字符串
            if "," in image_data:
                # 从data:image/png;base64,...格式中提取
                image_data = image_data.split(",", 1)[1]
            
            image_binary = base64.b64decode(image_data)
            
            # 生成唯一文件名
            file_name = f"{uuid.uuid4()}.png"
            file_path = os.path.join(upload_dir, file_name)
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(image_binary)
                
            return file_path
        except Exception as e:
            logger.error(f"保存图像时出错: {str(e)}")
            return None
    
    def get_detection(self, detection_id: int) -> Optional[Detection]:
        """通过ID获取一个检测记录"""
        return self.db.query(Detection).filter(Detection.id == detection_id).first()
    
    def list_detections(self,
                       page: int = 1,
                       per_page: int = 10,
                       search_text: Optional[str] = None,
                       status: Optional[str] = None,
                       date_from: Optional[datetime] = None,
                       date_to: Optional[datetime] = None,
                       device_id: Optional[int] = None,
                       operation_id: Optional[int] = None,
                       operation_type: Optional[str] = None,
                       confidence_min: Optional[float] = None,
                       confidence_max: Optional[float] = None) -> dict:
        """获取检测记录列表，带分页和过滤"""
        query = self.db.query(Detection)
        
        # 添加各种过滤条件
        if search_text:
            query = query.filter(Detection.text.ilike(f"%{search_text}%"))
            
        if status:
            # 处理前端传入的中文状态
            status_map = {
                "合格": DetectionStatus.PASS,
                "不合格": DetectionStatus.FAIL,
                "未知": DetectionStatus.UNKNOWN
            }
            if status in status_map:
                query = query.filter(Detection.status == status_map[status])
            elif status != "全部":  # 如果不是"全部"，直接使用传入值
                try:
                    query = query.filter(Detection.status == DetectionStatus(status))
                except ValueError:
                    # 无效状态值，忽略此过滤条件
                    pass
                
        if date_from:
            query = query.filter(Detection.timestamp >= date_from)
            
        if date_to:
            # 增加一天确保包含当天
            date_to = date_to + timedelta(days=1)
            query = query.filter(Detection.timestamp < date_to)
            
        if device_id:
            query = query.filter(Detection.device_id == device_id)
            
        if operation_id and operation_type:
            query = query.filter(
                Detection.operation_id == operation_id,
                Detection.operation_type == operation_type
            )
        
        if confidence_min is not None:
            query = query.filter(Detection.confidence >= confidence_min)
            
        if confidence_max is not None:
            query = query.filter(Detection.confidence <= confidence_max)
            
        # 计算总记录数
        total = query.count()
        
        # 应用排序和分页
        query = query.order_by(desc(Detection.timestamp))
        # query = query.offset((page - 1) * per_page).limit(per_page)
        
        # 获取结果
        detections = query.all()
        
        # 构建响应
        return {
            "items": detections,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
        
    def delete_detection(self, detection_id: int) -> bool:
        """删除一个检测记录"""
        detection = self.get_detection(detection_id)
        if not detection:
            return False
            
        # 删除关联的图像文件
        if detection.image_path and os.path.exists(detection.image_path):
            try:
                os.remove(detection.image_path)
            except Exception as e:
                logger.error(f"删除图像文件失败: {str(e)}")
                
        if detection.processed_image_path and os.path.exists(detection.processed_image_path):
            try:
                os.remove(detection.processed_image_path)
            except Exception as e:
                logger.error(f"删除处理后图像文件失败: {str(e)}")
                
        # 删除数据库记录
        self.db.delete(detection)
        self.db.commit()
        
        return True
        
    def clear_detections(self, 
                        before_date: Optional[datetime] = None, 
                        status: Optional[DetectionStatus] = None,
                        device_id: Optional[int] = None) -> int:
        """清除满足条件的检测记录"""
        query = self.db.query(Detection)
        
        # 添加过滤条件
        if before_date:
            query = query.filter(Detection.timestamp < before_date)
            
        if status:
            query = query.filter(Detection.status == status)
            
        if device_id:
            query = query.filter(Detection.device_id == device_id)
            
        # 获取要删除的记录
        detections_to_delete = query.all()
        count = len(detections_to_delete)
        
        # 删除关联的图像文件
        for detection in detections_to_delete:
            if detection.image_path and os.path.exists(detection.image_path):
                try:
                    os.remove(detection.image_path)
                except Exception as e:
                    logger.error(f"删除图像文件失败: {str(e)}")
                    
            if detection.processed_image_path and os.path.exists(detection.processed_image_path):
                try:
                    os.remove(detection.processed_image_path)
                except Exception as e:
                    logger.error(f"删除处理后图像文件失败: {str(e)}")
            
            # 删除数据库记录
            self.db.delete(detection)
            
        self.db.commit()
        
        return count

# 创建单例服务实例
def get_detection_service(db: Session = next(get_db())):
    return DetectionService(db)

detection_service = DetectionService(next(get_db())) 