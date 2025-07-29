from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Body
from sqlalchemy.orm import Session
from ..services.annotation import AnnotationService
from ..models import DatasetType
from ..dependencies import get_db
from typing import List, Dict, Any
from datetime import datetime
import os
from pydantic import Field, validator
from ..routers.base import CamelModel

router = APIRouter(prefix="/api/annotation", tags=["annotation"])

class AnnotationResponse(CamelModel):
    """标注数据基础模型"""
    annotations: List[Dict[str, Any]] = Field(default_factory=list, description="标注标签列表")

class DatasetResponse(CamelModel):
    id: int = Field(..., description="数据集ID")
    name: str = Field(..., min_length=1, max_length=100, description="数据集名称")
    type: DatasetType = Field(..., description="数据集类型")
    imageCount: int = Field(..., description="图片数量")
    createdAt: datetime = Field(..., description="创建时间")
    updatedAt: datetime = Field(..., description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "文本区域标注数据集",
                "type": "TEXT_REGION",
                "imageCount": 100,
                "createdAt": "2024-03-22T10:00:00",
                "updatedAt": "2024-03-22T10:00:00"
            }
        }

class ImageResponse(CamelModel):
    id: int = Field(..., description="图片ID")
    filename: str = Field(..., description="文件名")
    url: str = Field(..., description="图片URL")
    datasetId: int = Field(..., description="所属数据集ID")
    createdAt: datetime = Field(..., description="创建时间")
    isAnnotated: bool = Field(False, description="是否已标注")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "filename": "example.jpg",
                "url": "/uploads/1/example.jpg",
                "datasetId": 1,
                "createdAt": "2024-03-22T10:00:00",
                "isAnnotated": False
            }
        }

# --- 请求模型 ---
class CreateDatasetRequest(CamelModel):
    name: str = Field(..., min_length=1, max_length=100, description="数据集名称")
    type: DatasetType = Field(default=DatasetType.TEXT_REGION, description="数据集类型")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("数据集名称不能为空")
        return v.strip()

class UpdateDatasetRequest(CamelModel):
    name: str = Field(..., min_length=1, max_length=100, description="数据集名称")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("数据集名称不能为空")
        return v.strip()

class AnnotationRequest(CamelModel):
    annotations: List[Dict[str, Any]] = Field(..., description="标注数据")

    @validator('annotations')
    def validate_annotations(cls, v):
        if not isinstance(v, list):
            raise ValueError("标注数据必须是列表")
        return v

# --- 路由处理函数 ---
@router.get("/datasets", response_model=List[DatasetResponse])
async def get_datasets(db: Session = Depends(get_db)):
    """获取所有数据集"""
    service = AnnotationService(db)
    datasets = service.get_datasets()
    
    return [
        DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            type=dataset.type,
            imageCount=len(dataset.images),
            createdAt=dataset.created_at,
            updatedAt=dataset.updated_at
        )
        for dataset in datasets
    ]

@router.post("/datasets", response_model=DatasetResponse)
async def create_dataset(
    request: CreateDatasetRequest,
    db: Session = Depends(get_db)
):
    """创建新数据集"""
    service = AnnotationService(db)
    try:
        dataset = service.create_dataset(request.name, request.type)
        return DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            type=dataset.type,
            imageCount=len(dataset.images),
            createdAt=dataset.created_at,
            updatedAt=dataset.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create dataset: {str(e)}"
        )

@router.put("/datasets/{dataset_id}", response_model=DatasetResponse)
async def rename_dataset(
    dataset_id: int,
    request: UpdateDatasetRequest,
    db: Session = Depends(get_db)
):
    """重命名数据集"""
    service = AnnotationService(db)
    try:
        dataset = service.rename_dataset(dataset_id, request.name)
        return DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            type=dataset.type,
            imageCount=len(dataset.images),
            createdAt=dataset.created_at,
            updatedAt=dataset.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to rename dataset: {str(e)}"
        )

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """删除数据集"""
    service = AnnotationService(db)
    service.delete_dataset(dataset_id)
    return {"status": "success"}

@router.get("/datasets/{dataset_id}/images", response_model=List[ImageResponse])
async def get_dataset_images(dataset_id: int, db: Session = Depends(get_db)):
    """获取数据集下的所有图片"""
    service = AnnotationService(db)
    try:
        images = service.get_dataset_images(dataset_id)
        return [
            ImageResponse(
                id=image.id,
                filename=image.filename,
                url=f"/uploads/{dataset_id}/{image.filename}",
                isAnnotated=image.is_annotated,
                datasetId=image.dataset_id,
                createdAt=image.created_at
            )
            for image in images
        ]
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get images: {str(e)}"
        )

@router.post("/datasets/{dataset_id}/images", response_model=List[ImageResponse])
async def upload_images(
    dataset_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """上传图片到数据集"""
    service = AnnotationService(db)
    uploaded_images = []
    
    try:
        # 确保上传目录存在
        upload_dir = os.path.join("uploads", str(dataset_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        for file in files:
            # 生成安全的文件名
            filename = file.filename
            file_path = os.path.join(upload_dir, filename)
            
            # 保存文件
            try:
                contents = await file.read()
                with open(file_path, "wb") as f:
                    f.write(contents)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to save file {filename}: {str(e)}"
                )
            
            # 保存到数据库
            try:
                url = f"/uploads/{dataset_id}/{filename}"
                image = service.create_image(
                    dataset_id=dataset_id,
                    filename=filename,
                    url=url
                )
                uploaded_images.append(
                    ImageResponse(
                        id=image.id,
                        filename=image.filename,
                        url=url,
                        datasetId=image.dataset_id,
                        createdAt=image.created_at,
                        isAnnotated=image.is_annotated
                    )
                )
            except Exception as e:
                # 如果数据库保存失败，删除已上传的文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
                
        return uploaded_images
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload images: {str(e)}"
        )

@router.delete("/images/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    """删除图片"""
    service = AnnotationService(db)
    service.delete_image(image_id)
    return {"status": "success"}

@router.get("/images/{image_id}/annotation", response_model=AnnotationResponse)
async def get_image_annotation(image_id: int, db: Session = Depends(get_db)):
    """获取图片的标注数据"""
    service = AnnotationService(db)
    try:
        annotation = service.get_image_annotation(image_id)
        if annotation:
            return AnnotationResponse(
                annotations=annotation.get("annotations", []),
                status=annotation.get("status", "pending")
            )
        return AnnotationResponse()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get annotation: {str(e)}"
        )

@router.post("/images/{image_id}/annotation", response_model=AnnotationResponse)
async def save_annotation(
    image_id: int,
    request: AnnotationRequest,
    db: Session = Depends(get_db)
):
    """创建标注数据"""
    service = AnnotationService(db)
    try:
        annotation = service.save_annotation(image_id, request.dict())
        return AnnotationResponse(**annotation.data)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create annotation: {str(e)}"
        )
