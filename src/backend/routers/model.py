from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request, Response
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from ..dependencies import get_db
from ..models import ModelArchitecture
from ..services.model import ModelService
from pydantic import BaseModel
from datetime import datetime
import time
import logging
from ..common.globals import TRAINING_LOGS  # 从全局模块导入
import base64
import io
import os
import json
from pathlib import Path
import numpy as np
from PIL import Image as PILImage

# 获取logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/models",
    tags=["models"]
)

# Pydantic models for request/response
class ModelCreate(BaseModel):
    name: str
    architecture: ModelArchitecture
    dataset_id: int
    parameters: Optional[Dict[str, Any]] = None
    
class ModelUpdate(BaseModel):
    name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    
class ModelResponse(BaseModel):
    id: int
    name: str
    architecture: str
    dataset_id: int
    status: str
    parameters: Dict[str, Any]
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    file_path: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

# 文件浏览相关模型
class FileInfo(BaseModel):
    name: str
    path: str
    isDir: bool
    size: int
    modifiedTime: str

class FileListResponse(BaseModel):
    files: List[FileInfo]

class FileContentResponse(BaseModel):
    content: str

@router.get("/", response_model=List[ModelResponse])
def get_models(db: Session = Depends(get_db)):
    service = ModelService(db)
    return service.get_models()

@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    service = ModelService(db)
    model = service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@router.post("/", response_model=ModelResponse)
def create_model(model: ModelCreate, db: Session = Depends(get_db)):
    service = ModelService(db)
    return service.create_model(
        name=model.name,
        architecture=model.architecture,
        dataset_id=model.dataset_id,
        parameters=model.parameters
    )

@router.put("/{model_id}", response_model=ModelResponse)
def update_model(model_id: int, model: ModelUpdate, db: Session = Depends(get_db)):
    service = ModelService(db)
    return service.update_model(
        model_id=model_id,
        **model.dict(exclude_unset=True)
    )

@router.delete("/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    service = ModelService(db)
    service.delete_model(model_id)
    return {"message": "Model deleted successfully"}

@router.post("/{model_id}/train", response_model=ModelResponse)
def start_training(model_id: int, db: Session = Depends(get_db)):
    service = ModelService(db)
    return service.start_training(model_id)

@router.get("/{model_id}/export")
def export_model(model_id: int, db: Session = Depends(get_db)):
    service = ModelService(db)
    export_path = service.export_model(model_id)
    return {"message": "Model exported successfully", "file_path": export_path}

# 采用base64图像方式测试模型
class TestModelRequest(BaseModel):
    image_base64: str  # base64编码的图像
    conf_thres: float = 0.25
    iou_thres: float = 0.45

@router.post("/{model_id}/test")
async def test_model_base64(
    model_id: int,
    request: TestModelRequest,
    db: Session = Depends(get_db)
):
    """
    使用训练好的模型测试base64编码的图像。
    返回检测结果和处理后的图像
    """
    import cv2
    
    service = ModelService(db)
    
    try:
        # 解码base64图像数据
        try:
            # 检查是否包含data:image前缀
            if "base64," in request.image_base64:
                image_data = request.image_base64.split("base64,")[1]
            else:
                image_data = request.image_base64
                
            # 解码base64
            image_bytes = base64.b64decode(image_data)
            
            # 转换为numpy数组
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "无法解码图像数据"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": f"图像解码失败: {str(e)}"}
            )
            
        # 使用模型进行预测直接传递numpy数组
        annotated_image, detections = service.test_model_image(
            model_id=model_id,
            image=img,
            conf_thres=request.conf_thres,
            iou_thres=request.iou_thres
        )
        
        # 将结果图像编码为base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # 返回结果
        return {
            "success": True,
            "detections": detections,
            "image": f"data:image/jpeg;base64,{image_base64}"
        }
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@router.get("/{model_id}/logs")
def get_model_logs(model_id: int, db: Session = Depends(get_db)):
    """获取模型训练日志"""
    service = ModelService(db)
    model = service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # 从全局字典获取训练日志
    logs = []
    if model_id in TRAINING_LOGS:
        logs = TRAINING_LOGS[model_id]
    else:
        # 如果没有日志，添加一条信息
        timestamp = time.strftime("%H:%M:%S")
        logs.append(f"[{timestamp}] 等待训练日志...")
    
    return {"model_id": model_id, "logs": logs}

# 获取模型文件列表
@router.get("/{model_id}/files", response_model=FileListResponse)
def get_model_files(model_id: int, path: str = "", db: Session = Depends(get_db)):
    service = ModelService(db)
    model = service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    # 构建模型目录路径 - 与训练代码中保持一致
    project_dir = "models"
    name = f"model_{model_id}"
    model_dir = os.path.abspath(os.path.join(project_dir, name))
    
    # 调试日志
    logger.info(f"模型文件请求: 模型ID={model_id}, 相对路径='{path}'")
    logger.info(f"完整模型目录: {model_dir}")
    
    # 验证模型目录存在
    if not os.path.exists(model_dir):
        logger.error(f"模型目录不存在: {model_dir}")
        # 检查父目录结构
        logger.info(f"项目目录: {os.path.abspath(project_dir)}")
        if os.path.exists(project_dir):
            logger.info(f"项目目录内容: {os.listdir(project_dir)}")
        raise HTTPException(status_code=404, detail=f"Model {model_id} directory not found")
    
    # 构建目标路径
    target_path = os.path.join(model_dir, path)
    logger.info(f"目标路径: {target_path}")
    
    # 验证路径安全性（防止目录遍历）
    if not os.path.abspath(target_path).startswith(os.path.abspath(model_dir)):
        raise HTTPException(status_code=403, detail="Access denied: Path traversal attempt detected")
    
    # 验证路径存在
    if not os.path.exists(target_path):
        logger.error(f"路径不存在: {target_path}")
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    
    # 如果是目录，列出内容
    if os.path.isdir(target_path):
        files = []
        logger.info(f"读取目录内容: {target_path}")
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            rel_path = os.path.relpath(item_path, model_dir)
            
            # 获取文件/目录信息
            stat = os.stat(item_path)
            files.append(FileInfo(
                name=item,
                path=rel_path,
                isDir=os.path.isdir(item_path),
                size=stat.st_size,
                modifiedTime=datetime.fromtimestamp(stat.st_mtime).isoformat()
            ))
        
        logger.info(f"找到 {len(files)} 个文件/目录")
        return FileListResponse(files=files)
    else:
        raise HTTPException(status_code=400, detail="Path is not a directory")

# 获取文件内容 (用于文本文件)
@router.get("/{model_id}/files/content", response_model=FileContentResponse)
def get_file_content(model_id: int, path: str, db: Session = Depends(get_db)):
    service = ModelService(db)
    model = service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    # 构建模型目录路径
    project_dir = "models"
    name = f"model_{model_id}"
    model_dir = os.path.abspath(os.path.join(project_dir, name))
    
    # 构建目标路径
    target_path = os.path.join(model_dir, path)
    
    # 验证路径安全性
    if not os.path.abspath(target_path).startswith(os.path.abspath(model_dir)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 验证文件存在且不是目录
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    if os.path.isdir(target_path):
        raise HTTPException(status_code=400, detail="Path is a directory, not a file")
    
    # 检查文件类型（只读取文本文件）
    text_extensions = ['.txt', '.csv', '.yaml', '.yml', '.json', '.log', '.md']
    if not any(target_path.lower().endswith(ext) for ext in text_extensions):
        raise HTTPException(status_code=400, detail="File type not supported for text reading")
    
    # 读取文件内容
    try:
        with open(target_path, 'r') as file:
            content = file.read()
        return FileContentResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

# 预览文件（用于图像文件）
@router.get("/{model_id}/files/preview")
def preview_file(model_id: int, path: str, db: Session = Depends(get_db)):
    service = ModelService(db)
    model = service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    # 构建模型目录路径
    project_dir = "models"
    name = f"model_{model_id}"
    model_dir = os.path.abspath(os.path.join(project_dir, name))
    
    # 构建目标路径
    target_path = os.path.join(model_dir, path)
    
    # 验证路径安全性
    if not os.path.abspath(target_path).startswith(os.path.abspath(model_dir)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 验证文件存在且不是目录
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    if os.path.isdir(target_path):
        raise HTTPException(status_code=400, detail="Path is a directory, not a file")
    
    # 检查文件类型（只预览图像文件）
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    if not any(target_path.lower().endswith(ext) for ext in image_extensions):
        raise HTTPException(status_code=400, detail="File type not supported for preview")
    
    # 返回图像文件
    return FileResponse(
        target_path,
        media_type=f"image/{os.path.splitext(target_path)[1][1:]}",
        filename=os.path.basename(target_path)
    )

# 下载文件
@router.get("/{model_id}/files/download")
def download_file(model_id: int, path: str, db: Session = Depends(get_db)):
    service = ModelService(db)
    model = service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    # 构建模型目录路径
    project_dir = "models"
    name = f"model_{model_id}"
    model_dir = os.path.abspath(os.path.join(project_dir, name))
    
    # 构建目标路径
    target_path = os.path.join(model_dir, path)
    
    # 验证路径安全性
    if not os.path.abspath(target_path).startswith(os.path.abspath(model_dir)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 验证文件存在且不是目录
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    if os.path.isdir(target_path):
        raise HTTPException(status_code=400, detail="Path is a directory, not a file")
    
    # 返回文件供下载
    return FileResponse(
        target_path,
        media_type="application/octet-stream",
        filename=os.path.basename(target_path)
    ) 