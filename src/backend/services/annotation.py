from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import Dataset, Image, Annotation, DatasetType
from datetime import datetime
from typing import List, Optional
import os

class AnnotationService:
    def __init__(self, db: Session):
        self.db = db

    def get_datasets(self) -> List[Dataset]:
        return self.db.query(Dataset).all()

    def create_dataset(self, name: str, type: DatasetType = DatasetType.TEXT_REGION) -> Dataset:
        try:
            dataset = Dataset(
                name=name,
                type=type
            )
            self.db.add(dataset)
            self.db.commit()
            self.db.refresh(dataset)
            return dataset
        except Exception as e:
            self.db.rollback()
            raise e

    def rename_dataset(self, dataset_id: int, new_name: str) -> Dataset:
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        dataset.name = new_name
        dataset.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def delete_dataset(self, dataset_id: int):
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        self.db.delete(dataset)
        self.db.commit()

    def get_dataset_images(self, dataset_id: int) -> List[Image]:
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset.images

    def create_image(self, dataset_id: int, filename: str, url: str) -> Image:
        """创建新图片"""
        try:
            # 检查数据集是否存在
            dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            image = Image(
                filename=filename,
                url=url,
                dataset_id=dataset_id,
                created_at=datetime.utcnow(),
                is_annotated=False
            )
            self.db.add(image)
            self.db.commit()
            self.db.refresh(image)
            return image
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_image(self, image_id: int):
        """删除图片"""
        image = self.db.query(Image).filter(Image.id == image_id).first()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        try:
            # 从 url 中获取文件路径
            # url 格式: /uploads/{dataset_id}/{filename}
            file_path = os.path.join(".", image.url.lstrip('/'))
            
            # 删除物理文件
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 删除数据库记录
            self.db.delete(image)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete image: {str(e)}"
            )

    def get_image_annotation(self, image_id: int) -> Optional[dict]:
        try:
            # Changed to get the single annotation for the image
            ann = self.db.query(Annotation).filter(Annotation.image_id == image_id).first()
            if not ann:
                return None
            
            return ann.data
        except Exception as e:
            raise e

    def save_annotation(self, image_id: int, annotation_data: dict) -> Annotation:
        try:
            # Check if image exists
            image = self.db.query(Image).filter(Image.id == image_id).first()
            if not image:
                raise HTTPException(status_code=404, detail="Image not found")
            
            # Check if annotation already exists for this image
            existing_annotation = self.db.query(Annotation).filter(
                Annotation.image_id == image_id
            ).first()
            
            if existing_annotation:
                # Update existing annotation instead of creating a new one
                existing_annotation.data = annotation_data
                existing_annotation.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing_annotation)
                
                # Update image annotation status
                if len(annotation_data.get('annotations', [])) == 0:
                    image.is_annotated = False
                else:
                    image.is_annotated = True
                self.db.commit()
                
                return existing_annotation
            
            # Create new annotation if none exists
            annotation = Annotation(
                image_id=image_id,
                data=annotation_data
            )
            self.db.add(annotation)
            self.db.commit()
            self.db.refresh(annotation)

            # Update image annotation status
            image.is_annotated = True
            self.db.commit()

            return annotation
        except Exception as e:
            self.db.rollback()
            raise e
