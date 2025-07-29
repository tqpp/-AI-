from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import Model, Dataset, ModelStatus, ModelArchitecture, DatasetType, Image
from datetime import datetime
from typing import List, Optional, Dict, Any, Union, Tuple
import os
import json
import logging
import numpy as np
import cv2
import shutil
import torch
import urllib.request
import time
import random
import queue
import threading
import subprocess
import re
from sqlalchemy.orm import sessionmaker
from ..models.base import engine
from ..common.globals import TRAINING_LOGS
import sys

# 设置日志
logger = logging.getLogger(__name__)

class YOLOModel:
    """YOLO模型包装类，用于在cv_operation中使用"""
    
    def __init__(self, model_path: str, architecture: ModelArchitecture):
        """
        初始化YOLO模型
        
        Args:
            model_path: 模型文件路径
            architecture: 模型架构类型
        """
        self.model_path = model_path
        self.architecture = architecture
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.load_model()
        
    def load_model(self):
        """加载模型"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"模型文件不存在: {self.model_path}")
            
        try:
            if self.architecture == ModelArchitecture.YOLO_V5:
                current_dir = os.getcwd()
                yolov5_path = os.path.join(current_dir, 'yolov5')
                print(yolov5_path)
                # 使用YOLOv5加载模型
                self.model = torch.hub.load(yolov5_path, 'custom', path=self.model_path, source="local")
            elif self.architecture == ModelArchitecture.YOLO_V8:
                # 使用YOLOv8加载模型
                from ultralytics import YOLO
                print(self.model_path)
                self.model = YOLO(self.model_path)
            elif self.architecture == ModelArchitecture.YOLO_V9:
                # 使用YOLOv9加载模型
                from ultralytics import YOLO
                self.model = YOLO(self.model_path)
            else:
                raise ValueError(f"不支持的模型架构: {self.architecture}")
                
            # 设置设备
            self.model.to(self.device)
            logger.info(f"模型加载成功: {self.model_path}, 架构: {self.architecture}, 设备: {self.device}")
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise RuntimeError(f"模型加载失败: {str(e)}")
            
    def predict(self, image: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        使用模型预测图像
        
        Args:
            image: 输入图像
            
        Returns:
            Tuple[标注好的图像, 检测结果列表]
        """
        if self.model is None:
            raise RuntimeError("模型未加载")
            
        try:
            # 执行推理
            results = self.model(image)
            
            # 获取结果
            if self.architecture == ModelArchitecture.YOLO_V5:
                # YOLOv5结果处理
                detections = []
                for *xyxy, conf, cls in results.xyxy[0]:
                    x1, y1, x2, y2 = map(float, xyxy)
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': float(conf),
                        'class_id': int(cls),
                        'class_name': results.names[int(cls)]
                    })
                # 获取标注图像
                annotated_img = results.render()[0]
            else:
                # YOLOv8/v9结果处理
                detections = []
                boxes = results[0].boxes
                for i, box in enumerate(boxes):
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': conf,
                        'class_id': cls_id,
                        'class_name': results[0].names[cls_id]
                    })
                # 获取标注图像
                annotated_img = results[0].plot()
                
            return annotated_img, detections
        except Exception as e:
            logger.error(f"模型预测失败: {str(e)}")
            raise RuntimeError(f"模型预测失败: {str(e)}")
            
class ModelService:
    def __init__(self, db: Session):
        self.db = db
        self._loaded_models = {}  # 缓存已加载的模型

    def get_model_instance(self, model_id: int) -> YOLOModel:
        """
        获取模型实例，用于在cv_operation中使用
        
        Args:
            model_id: 模型ID
            
        Returns:
            YOLOModel实例
        """
        # 检查缓存
        if model_id in self._loaded_models:
            logger.info(f"从缓存获取模型 {model_id}")
            # 返回缓存的模型实例的副本，避免线程安全问题
            try:
                # 检查模型是否有效
                cached_model = self._loaded_models[model_id]
                # 简单校验以确保模型没有损坏
                if not hasattr(cached_model, 'model') or cached_model.model is None:
                    logger.warning(f"缓存的模型 {model_id} 已损坏，重新加载")
                    # 删除缓存中的无效模型
                    del self._loaded_models[model_id]
                    # 继续执行重新加载逻辑
                else:
                    return cached_model
            except Exception as e:
                logger.warning(f"访问缓存模型 {model_id} 时出错: {str(e)}，重新加载")
                # 删除缓存中的无效模型
                del self._loaded_models[model_id]
                # 继续执行重新加载逻辑
            
        # 获取模型信息
        model = self.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
            
        # 检查模型是否已完成训练
        if model.status != ModelStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Model training not completed")
            
        # 检查模型文件是否存在
        if not model.file_path or not os.path.exists(model.file_path):
            raise HTTPException(status_code=400, detail="Model file not found")
            
        try:
            # 创建模型实例
            logger.info(f"加载模型 {model_id}: {model.file_path}")
            yolo_model = YOLOModel(model.file_path, model.architecture)
            # 缓存模型
            self._loaded_models[model_id] = yolo_model
            return yolo_model
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
            
    def get_models(self) -> List[Model]:
        """获取所有模型"""
        return self.db.query(Model).all()
        
    def get_models_by_dataset(self, dataset_id: int) -> List[Model]:
        """获取特定数据集的所有模型"""
        return self.db.query(Model).filter(Model.dataset_id == dataset_id).all()

    def get_model(self, model_id: int) -> Optional[Model]:
        """获取指定模型"""
        return self.db.query(Model).filter(Model.id == model_id).first()

    def create_model(self, 
                    name: str, 
                    architecture: ModelArchitecture,
                    dataset_id: int,
                    parameters: Dict[str, Any] = None) -> Model:
        """创建新模型"""
        try:
            # 检查数据集是否存在
            dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")
                
            # 验证参数
            if parameters is None:
                parameters = {}
                
            # 根据架构类型设置默认参数
            if 'epochs' not in parameters:
                parameters['epochs'] = 50
            if 'batch_size' not in parameters:
                parameters['batch_size'] = 16
            if 'img_size' not in parameters:
                parameters['img_size'] = 640
            if 'conf_thres' not in parameters:
                parameters['conf_thres'] = 0.25
            if 'iou_thres' not in parameters:
                parameters['iou_thres'] = 0.45
                
            model = Model(
                name=name,
                architecture=architecture,
                dataset_id=dataset_id,
                status=ModelStatus.NOT_STARTED,
                parameters=parameters,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return model
        except Exception as e:
            self.db.rollback()
            raise e

    def update_model(self, model_id: int, **kwargs) -> Model:
        """更新模型信息"""
        model = self.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
            
        # 更新提供的字段
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
                
        model.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(model)
            return model
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_model(self, model_id: int) -> None:
        """删除模型"""
        model = self.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
            
        try:
            # 如果有模型文件，尝试删除
            if model.file_path and os.path.exists(model.file_path):
                os.remove(model.file_path)
            
            # 从缓存中删除
            if model_id in self._loaded_models:
                del self._loaded_models[model_id]
                
            self.db.delete(model)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def start_training(self, model_id: int) -> Model:
        """启动模型训练"""
        model = self.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
            
        # 检查模型状态，如果已经在训练则返回错误
        if model.status == ModelStatus.TRAINING:
            raise HTTPException(status_code=400, detail="Model is already training")
            
        # 更新模型状态为训练中
        model.status = ModelStatus.TRAINING
        model.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(model)
            
            # 获取数据集ID用于线程中
            dataset_id = model.dataset_id
            
            # 这里在实际应用中，应该启动一个后台任务来执行训练
            # 为了简化示例，我们直接在一个新线程中执行训练
            import threading
            thread = threading.Thread(target=self._train_model, args=(model_id, dataset_id))
            thread.daemon = True
            thread.start()
            
            return model
        except Exception as e:
            self.db.rollback()
            raise e
            
    def _train_model(self, model_id: int, dataset_id: int) -> None:
        """实际的模型训练过程"""
        # 创建新的数据库会话
        from sqlalchemy.orm import sessionmaker
        from ..models.base import engine
        
        Session = sessionmaker(engine)
        db = None
        
        try:
            db = Session()
            
            # 使用新会话获取模型信息
            model = db.query(Model).filter(Model.id == model_id).first()
            if not model:
                logger.error(f"模型不存在: {model_id}")
                return
                
            # 获取数据集信息
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                logger.error(f"数据集不存在: {dataset_id}")
                self._update_training_status(model_id, ModelStatus.FAILED, 
                    error_message="Dataset not found")
                return
                
            # 预加载数据集的图像和标注
            from sqlalchemy.orm import joinedload
            images = db.query(Image).options(
                joinedload(Image.annotation)
            ).filter(Image.dataset_id == dataset_id).all()
            
            # 关闭数据库连接，预处理阶段结束
            db.close()
            db = None
            
            # 确保图像有file_path属性
            for image in images:
                # 如果image对象没有file_path属性，使用url作为文件路径
                if not hasattr(image, 'file_path'):
                    image.file_path = image.url
            
            # 准备数据集
            dataset_dir = self._prepare_dataset_for_yolo(dataset, images)
            
            # 根据模型架构选择训练方法
            try:
                # 获取模型训练参数
                logger.info(f"开始训练模型 ID:{model_id}, 架构:{model.architecture}")
                if model.architecture in [ModelArchitecture.YOLO_V8, ModelArchitecture.YOLO_V9]:
                    success = self._run_yolo_training(model_id, dataset_dir, model.parameters, "YOLOv8")
                elif model.architecture == ModelArchitecture.YOLO_V5:
                    success = self._run_yolo_training(model_id, dataset_dir, model.parameters, "YOLOv5")
                else:
                    logger.error(f"不支持的模型架构: {model.architecture}")
                    self._update_training_status(model_id, ModelStatus.FAILED, 
                        error_message=f"Unsupported model architecture: {model.architecture}")
                    return
                
                if not success:
                    logger.error(f"模型训练失败: {model_id}")
            except Exception as e:
                logger.error(f"模型训练过程中发生异常: {str(e)}", exc_info=True)
                self._update_training_status(model_id, ModelStatus.FAILED, 
                    error_message=str(e))
                
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            self._update_training_status(model_id, ModelStatus.FAILED, 
                error_message=str(e))
        finally:
            # 确保关闭会话
            if db:
                try:
                    db.close()
                except:
                    pass

    def _run_yolo_training(self, model_id: int, dataset_dir: str, parameters: dict, model_type: str) -> bool:
        """运行YOLO训练任务，统一处理YOLOv5和YOLOv8的训练逻辑
        
        Args:
            model_id: 模型ID
            dataset_dir: 数据集目录
            parameters: 训练参数
            model_type: "YOLOv5" 或 "YOLOv8"
            
        Returns:
            bool: 训练是否成功
        """
        try:
            # 初始化日志列表
            TRAINING_LOGS[model_id] = []
            
            # 添加初始日志
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            TRAINING_LOGS[model_id].append(f"[{timestamp}] [系统] 开始{model_type}训练...")
            
            # 提取训练参数
            epochs = parameters.get('epochs', 20)
            batch_size = parameters.get('batch_size', 8)
            img_size = parameters.get('img_size', 640)
            
            # 记录训练参数
            TRAINING_LOGS[model_id].append(f"[{timestamp}] [系统] 训练参数: epochs={epochs}, batch_size={batch_size}, img_size={img_size}")
            
            # 设置训练基本参数
            data_yaml_path = os.path.join(dataset_dir, "dataset.yaml")
            project_dir = "models"
            name = f"model_{model_id}"
            
            # 创建工作目录
            os.makedirs(os.path.join(project_dir, name), exist_ok=True)
            
            # 准备训练命令 - 不同模型有不同命令格式
            if model_type == "YOLOv8":
                cmd = [
                    "yolo",
                    "task=detect",
                    "mode=train",
                    f"data={os.path.abspath(data_yaml_path)}",
                    "model=yolov8n.pt", 
                    f"epochs={epochs}",
                    f"batch={batch_size}",
                    f"imgsz={img_size}",
                    f"project={project_dir}",
                    f"name={name}",
                    "exist_ok=True",
                    "device=cpu"
                ]
            elif model_type == "YOLOv5":
                # 确保YOLOv5代码存在
                yolov5_dir = "yolov5"
                if not os.path.exists(yolov5_dir):
                    subprocess.run(["git", "clone", "https://github.com/ultralytics/yolov5.git"])
                    
                # 将YOLOv5目录添加到路径    
                if yolov5_dir not in sys.path:
                    sys.path.append(yolov5_dir)
                    
                cmd = [
                    "python", f"{yolov5_dir}/train.py",
                    "--img", str(img_size),
                    "--batch", str(batch_size),
                    "--epochs", str(epochs),
                    "--data", data_yaml_path,
                    "--weights", "yolov5s.pt",
                    "--project", project_dir,
                    "--name", name,
                    "--exist-ok",
                    "--device", "cpu"
                ]
            else:
                logger.error(f"不支持的YOLO模型类型: {model_type}")
                return False
            
            # 打印命令行 
            cmd_str = ' '.join(cmd)
            logger.info(f"执行{model_type}训练命令: {cmd_str}")
            TRAINING_LOGS[model_id].append(f"[{timestamp}] [系统] 执行命令: {cmd_str}")
            
            # 记录开始时间
            start_time = time.time()
            
            # 使用Popen执行命令并捕获输出
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # 创建线程来读取stdout和stderr
            def read_output(stream, log_type):
                for line in iter(stream.readline, ''):
                    if line.strip():
                        timestamp = time.strftime("%H:%M:%S", time.localtime())
                        log_entry = f"[{timestamp}] [{log_type}] {line.strip()}"
                        TRAINING_LOGS[model_id].append(log_entry)
                        # 保持日志数量在合理范围内
                        if len(TRAINING_LOGS[model_id]) > 1000:
                            TRAINING_LOGS[model_id] = TRAINING_LOGS[model_id][-1000:]
                        logger.info(log_entry)
                stream.close()
            
            # 启动读取线程
            stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "stdout"))
            stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "stderr"))
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            
            # 等待进程完成
            returncode = process.wait()
            
            # 等待线程完成
            stdout_thread.join()
            stderr_thread.join()
            
            # 记录训练结束信息
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            training_time = time.time() - start_time
            
            if returncode == 0:
                # 训练成功，更新模型状态
                best_model_path = os.path.join(project_dir, name, "weights", "best.pt")
                if os.path.exists(best_model_path):
                    self.update_model(model_id, 
                                    file_path=best_model_path, 
                                    status=ModelStatus.COMPLETED)
                    success_msg = f"{model_type}训练完成，耗时: {training_time:.1f}秒，模型保存在: {best_model_path}"
                    logger.info(success_msg)
                    TRAINING_LOGS[model_id].append(f"[{timestamp}] [系统] {success_msg}")
                    return True
                else:
                    error_msg = f"{model_type}训练完成但模型文件不存在"
                    logger.error(error_msg)
                    TRAINING_LOGS[model_id].append(f"[{timestamp}] [错误] {error_msg}")
                    self._update_training_status(model_id, ModelStatus.FAILED, 
                        error_message=f"{model_type} training completed but model file not found")
                    return False
            else:
                error_msg = f"{model_type}训练失败，返回码: {returncode}"
                logger.error(error_msg)
                TRAINING_LOGS[model_id].append(f"[{timestamp}] [错误] {error_msg}")
                self._update_training_status(model_id, ModelStatus.FAILED,
                    error_message=f"{model_type} training failed with return code: {returncode}")
                return False
                
        except Exception as e:
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            error_msg = f"{model_type}训练过程中发生异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if model_id in TRAINING_LOGS:
                TRAINING_LOGS[model_id].append(f"[{timestamp}] [错误] {error_msg}")
            self._update_training_status(model_id, ModelStatus.FAILED, 
                error_message=str(e))
            return False

    def _prepare_dataset_for_yolo(self, dataset: Dataset, images: List) -> str:
        """准备YOLO格式的数据集"""
        import os.path
        import urllib.request
        
        # 创建临时目录
        dataset_dir = os.path.join("data", "datasets", f"dataset_{dataset.id}")
        os.makedirs(dataset_dir, exist_ok=True)
        
        # 创建train, val目录
        train_dir = os.path.join(dataset_dir, "train")
        val_dir = os.path.join(dataset_dir, "val")
        os.makedirs(os.path.join(train_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(train_dir, "labels"), exist_ok=True)
        os.makedirs(os.path.join(val_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(val_dir, "labels"), exist_ok=True)
        
        logger.info(f"数据集图像数量: {len(images)}")
        
        # 拆分训练集和验证集
        # 处理小数据集的特殊情况
        if len(images) <= 1:
            # 如果只有一个样本，同时用于训练和验证
            logger.warning(f"数据集只有{len(images)}个样本，将同时用于训练和验证")
            train_images = images
            val_images = images
        elif len(images) <= 5:
            # 如果样本数量很少，使用1个样本作为验证集
            logger.warning(f"数据集只有{len(images)}个样本，将使用1个样本作为验证集")
            from random import sample
            val_idx = sample(range(len(images)), 1)[0]
            val_images = [images[val_idx]]
            train_images = [img for i, img in enumerate(images) if i != val_idx]
        else:
            # 正常情况，使用train_test_split
            from sklearn.model_selection import train_test_split
            train_images, val_images = train_test_split(images, test_size=0.2, random_state=42)
        
        logger.info(f"训练集: {len(train_images)}张图像, 验证集: {len(val_images)}张图像")
        
        # 处理训练集
        for image in train_images:
            # 复制图像
            img_path = os.path.join(train_dir, "images", f"{image.id}.jpg")
            self._save_image_to_path(image, img_path)
            
            # 更新图像的文件路径属性
            image.file_path = img_path
            
            # 创建YOLO格式的标注文件
            label_path = os.path.join(train_dir, "labels", f"{image.id}.txt")
            self._create_yolo_label(image, label_path)
            
        # 处理验证集
        for image in val_images:
            # 复制图像
            img_path = os.path.join(val_dir, "images", f"{image.id}.jpg")
            self._save_image_to_path(image, img_path)
            
            # 更新图像的文件路径属性
            image.file_path = img_path
            
            # 创建YOLO格式的标注文件
            label_path = os.path.join(val_dir, "labels", f"{image.id}.txt")
            self._create_yolo_label(image, label_path)
            
        # 创建数据集配置文件
        self._create_dataset_config(dataset, dataset_dir)
        
        return dataset_dir
        
    def _save_image_to_path(self, image, target_path: str) -> None:
        """将图像保存到指定路径，支持URL和本地文件路径"""
        try:
            # 记录详细日志
            logger.info(f"尝试复制图像ID={image.id}, 目标路径: {target_path}")
            logger.debug(f"图像对象属性: {dir(image)}")
            
            # 获取图像源路径
            source_path = None
            
            # 优先使用项目相对路径: uploads/{dataset_id}/{image.filename}
            if hasattr(image, 'dataset_id') and hasattr(image, 'filename') and image.filename:
                dataset_id = image.dataset_id
                # 相对路径版本
                relative_path = f"uploads/{dataset_id}/{image.filename}"
                if os.path.exists(relative_path):
                    source_path = relative_path
                    logger.info(f"使用相对路径格式: {source_path}")
            
            # 如果特定格式的路径不存在，尝试其他可能的路径
            if not source_path:
                if hasattr(image, 'file_path') and image.file_path and os.path.exists(image.file_path):
                    source_path = image.file_path
                    logger.info(f"使用file_path: {source_path}")
                elif hasattr(image, 'url') and image.url and os.path.exists(image.url):
                    source_path = image.url
                    logger.info(f"使用存在的本地url: {source_path}")
                elif hasattr(image, 'url') and image.url and image.url.startswith(('http://', 'https://')):
                    logger.info(f"使用远程URL: {image.url}")
                    try:
                        # 创建父目录
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        # 下载图像
                        urllib.request.urlretrieve(image.url, target_path)
                        logger.info(f"成功从URL下载: {image.url} -> {target_path}")
                        return
                    except Exception as e:
                        logger.error(f"下载图像失败: {str(e)}")
                        raise RuntimeError(f"Failed to download image: {str(e)}")
                    
            # 如果找不到图像源路径，尝试从已知位置查找
            if not source_path:
                # 尝试在标准位置搜索图像
                possible_paths = [
                    # 相对于项目根目录的标准路径
                    os.path.join("data", "images", f"{image.id}.jpg"),
                    os.path.join("data", "images", f"{image.id}.png"),
                    os.path.join("data", "uploads", f"{image.id}.jpg"),
                    os.path.join("data", "uploads", f"{image.id}.png"),
                    os.path.join("uploads", f"{image.id}.jpg"),
                    os.path.join("uploads", f"{image.id}.png"),
                    # 相对于数据集的路径
                    os.path.join("data", "datasets", f"dataset_{image.dataset_id}", "images", f"{image.id}.jpg"),
                    os.path.join("data", "datasets", f"dataset_{image.dataset_id}", "images", f"{image.id}.png"),
                    # 使用文件名搜索
                    os.path.join("data", "images", f"{image.filename}") if hasattr(image, 'filename') and image.filename else None,
                    os.path.join("data", "uploads", f"{image.filename}") if hasattr(image, 'filename') and image.filename else None,
                    os.path.join("uploads", f"{image.filename}") if hasattr(image, 'filename') and image.filename else None,
                ]
                
                # 过滤None值
                possible_paths = [p for p in possible_paths if p]
                
                # 尝试每一个可能的路径
                for path in possible_paths:
                    if os.path.exists(path):
                        source_path = path
                        logger.info(f"在目录中找到图像: {source_path}")
                        break
                        
            # 如果找到源路径，复制文件
            if source_path:
                try:
                    # 确保目标目录存在
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    # 复制图像
                    shutil.copy(source_path, target_path)
                    logger.info(f"成功复制图像: {source_path} -> {target_path}")
                    return
                except Exception as e:
                    logger.error(f"复制图像失败: {str(e)}")
                    raise RuntimeError(f"Failed to copy image: {str(e)}")
                    
            # 如果找不到图像，尝试创建一个空白图像
            logger.warning(f"无法找到图像 ID={image.id} 的任何源路径，创建空白图像")
            try:
                # 创建一个简单的空白图像
                blank_img = np.ones((640, 640, 3), dtype=np.uint8) * 255  # 白色背景
                # 在图像中心写入文本
                font = cv2.FONT_HERSHEY_SIMPLEX
                text = f"Image {image.id} not found"
                textsize = cv2.getTextSize(text, font, 1, 2)[0]
                x = (640 - textsize[0]) // 2
                y = (640 + textsize[1]) // 2
                cv2.putText(blank_img, text, (x, y), font, 1, (0, 0, 0), 2)
                
                # 确保目标目录存在
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                # 保存空白图像
                cv2.imwrite(target_path, blank_img)
                logger.info(f"创建空白图像: {target_path}")
                return
            except Exception as e:
                logger.error(f"创建空白图像失败: {str(e)}")
                raise RuntimeError(f"Failed to create blank image: {str(e)}")
                
        except FileNotFoundError as e:
            logger.error(f"图像未找到: {str(e)}")
            raise FileNotFoundError(f"Image not found: {image.id}")
        except Exception as e:
            logger.error(f"处理图像失败: {str(e)}")
            raise RuntimeError(f"Failed to process image: {str(e)}")
        
    def _create_yolo_label(self, image, label_path: str) -> None:
        """创建YOLO格式的标注文件，从W3C格式的标注转换为YOLO格式"""
        try:
            # 记录图像信息以便调试
            logger.info(f"处理图像标注: id={image.id}, 文件路径={image.file_path}")
            
            # 获取图像的标注数据
            if not hasattr(image, 'annotation'):
                logger.warning(f"图像{image.id}没有annotation属性")
                return
                
            # 获取标注对象
            annotation_obj = image.annotation
                
            logger.debug(f"标注类型: {type(annotation_obj)}")
            
            # 处理空标注情况
            if annotation_obj is None:
                logger.warning(f"图像{image.id}的标注为None")
                # 创建空的标注文件
                with open(label_path, 'w') as f:
                    pass
                return
            
            # 获取实际的标注数据
            annotation_data = None
            
            # 检查标注是集合还是单个对象
            if hasattr(annotation_obj, '__iter__') and not isinstance(annotation_obj, dict):
                # 多个标注对象的情况
                if len(annotation_obj) > 0:
                    # 取第一个标注对象的data
                    first_anno = annotation_obj[0]
                    if hasattr(first_anno, 'data'):
                        logger.debug(f"从集合中第一个标注获取data: {type(first_anno.data)}")
                        annotation_data = first_anno.data
            elif hasattr(annotation_obj, 'data'):
                # 单个标注对象
                logger.debug(f"从单个标注对象获取data: {type(annotation_obj.data)}")
                annotation_data = annotation_obj.data
            
            # 创建标注文件目录
            os.makedirs(os.path.dirname(label_path), exist_ok=True)
            
            # 处理标注数据
            annotation_found = False
            with open(label_path, 'w') as f:
                # 检查是否包含多个标注的数组
                if isinstance(annotation_data, dict) and 'annotations' in annotation_data:
                    annotations_array = annotation_data['annotations']
                    if annotations_array:
                        logger.info(f"找到{len(annotations_array)}个标注项")
                        # 处理所有标注
                        for anno_item in annotations_array:
                            if anno_item:
                                if self._process_annotation(f, image, anno_item):
                                    annotation_found = True
                    else:
                        logger.warning(f"图像{image.id}的annotations数组为空")
                else:
                    # 尝试处理单个标注数据
                    logger.warning(f"标注数据不是预期的{{'annotations': []}}格式，尝试直接处理")
                    if annotation_data and self._process_annotation(f, image, annotation_data):
                        annotation_found = True
            
            # 检查是否找到任何有效标注
            if not annotation_found:
                logger.warning(f"图像{image.id}没有找到有效的标注数据")
            else:
                logger.info(f"成功处理图像{image.id}的标注数据，已保存到{label_path}")
                
        except Exception as e:
            logger.error(f"创建YOLO标注文件失败: {str(e)}", exc_info=True)
            
    def _process_annotation(self, file_handler, image, annotation):
        """处理单个标注对象"""
        try:
            # 加载图像获取尺寸
            img = cv2.imread(image.file_path)
            if img is None:
                logger.error(f"无法读取图像: {image.file_path}")
                return False
                
            img_height, img_width = img.shape[:2]
            logger.debug(f"图像尺寸: {img_width}x{img_height}")
            
            # 记录标注信息
            logger.debug(f"标注ID: {annotation.get('id', 'unknown')}")
            
            # 检查标注格式是否符合预期
            if not isinstance(annotation, dict):
                logger.error(f"标注不是字典格式: {type(annotation)}")
                return False
                
            # 提取标注类型/标签
            label = None
            if 'body' in annotation and isinstance(annotation['body'], list) and len(annotation['body']) > 0:
                for body_item in annotation['body']:
                    if isinstance(body_item, dict) and 'value' in body_item:
                        label = body_item['value']
                        break
                        
            if label:
                logger.info(f"标注类型/标签: {label}")
            else:
                # 使用默认标签
                label = 'text'
                logger.info(f"未找到标签，使用默认值: {label}")
            
            # 检查target和selector
            if 'target' not in annotation or not isinstance(annotation['target'], dict):
                logger.error("标注中没有target字段或格式不正确")
                return False
                
            target = annotation['target']
            if 'selector' not in target or not isinstance(target['selector'], dict):
                logger.error("target中没有selector字段或格式不正确")
                return False
                
            selector = target['selector']
            selector_type = selector.get('type')
            
            if 'geometry' not in selector or not isinstance(selector['geometry'], dict):
                logger.error("selector中没有geometry字段或格式不正确")
                return False
                
            geometry = selector['geometry']
            
            # 确保标签被添加到类别映射中
            class_id = self._get_class_id_for_label(label)
            
            # 处理不同类型的选择器
            if selector_type == 'RECTANGLE':
                # 处理矩形
                if all(k in geometry for k in ('x', 'y', 'w', 'h')):
                    logger.debug(f"处理矩形: x={geometry['x']}, y={geometry['y']}, w={geometry['w']}, h={geometry['h']}")
                    return self._process_bbox_annotation(file_handler, 
                        {'x': geometry['x'], 'y': geometry['y'], 'width': geometry['w'], 'height': geometry['h']}, 
                        img_width, img_height, class_id)
            elif selector_type == 'POLYGON':
                # 处理多边形
                if 'points' in geometry and isinstance(geometry['points'], list):
                    logger.debug(f"处理多边形: {len(geometry['points'])}个点")
                    return self._compute_bounding_box(file_handler, geometry['points'], img_width, img_height, class_id)
            
            # 如果没有匹配的选择器类型，尝试通用处理
            # 尝试提取bounds信息
            if 'bounds' in geometry and isinstance(geometry['bounds'], dict):
                bounds = geometry['bounds']
                if all(k in bounds for k in ('minX', 'minY', 'maxX', 'maxY')):
                    logger.debug(f"使用bounds处理: minX={bounds['minX']}, minY={bounds['minY']}, maxX={bounds['maxX']}, maxY={bounds['maxY']}")
                    x = bounds['minX']
                    y = bounds['minY']
                    width = bounds['maxX'] - bounds['minX']
                    height = bounds['maxY'] - bounds['minY']
                    return self._process_bbox_annotation(file_handler,
                        {'x': x, 'y': y, 'width': width, 'height': height},
                        img_width, img_height, class_id)
            
            logger.warning(f"无法处理的标注格式: selector_type={selector_type}")
            return False
        except Exception as e:
            logger.error(f"处理标注失败: {str(e)}", exc_info=True)
            return False
            
    # 类别映射和相关方法
    _label_to_class_map = {}  # 缓存标签到类别ID的映射
    _class_names = []         # 保存所有类别名称的列表
    
    def _get_class_id_for_label(self, label):
        """获取或创建标签对应的类别ID"""
        if label not in self._label_to_class_map:
            # 新标签，添加到映射和列表中
            class_id = len(self._class_names)
            self._label_to_class_map[label] = class_id
            self._class_names.append(label)
            logger.info(f"添加新标签: '{label}' -> class_id {class_id}")
        return self._label_to_class_map[label]
    
    def _get_class_names(self):
        """获取所有类别名称列表"""
        # 确保至少有一个类别
        if not self._class_names:
            self._class_names = ['text']
            self._label_to_class_map['text'] = 0
        return self._class_names
            
    def _process_bbox_annotation(self, file_handler, bbox, img_width, img_height, class_id=0):
        """处理普通的边界框标注"""
        # 首先检查bbox是字典还是列表
        if isinstance(bbox, dict):
            # 字典格式：{x, y, width, height}
            x_min = float(bbox.get('x', 0))
            y_min = float(bbox.get('y', 0))
            width = float(bbox.get('width', 0))
            height = float(bbox.get('height', 0))
        elif isinstance(bbox, list) and len(bbox) >= 4:
            # 列表格式：[x, y, width, height] 或 [x1, y1, x2, y2]
            if len(bbox) == 4:
                # 可能是[x, y, width, height]或[x1, y1, x2, y2]
                if bbox[2] < bbox[0] or bbox[3] < bbox[1]:
                    # 如果第三个值小于第一个值，第四个值小于第二个值，则认为是[x1, y1, x2, y2]格式
                    x_min = float(bbox[0])
                    y_min = float(bbox[1])
                    width = float(bbox[2] - bbox[0])
                    height = float(bbox[3] - bbox[1])
                else:
                    # 否则认为是[x, y, width, height]格式
                    x_min = float(bbox[0])
                    y_min = float(bbox[1])
                    width = float(bbox[2])
                    height = float(bbox[3])
        else:
            logger.error(f"无法识别的bbox格式: {bbox}")
            return False
        
        # 检查坐标和尺寸是否有效
        if width <= 0 or height <= 0:
            logger.error(f"无效的bbox尺寸: width={width}, height={height}")
            return False
            
        # 转换为YOLO格式 (x_center, y_center, width, height)，归一化到[0,1]
        x_center = (x_min + width / 2) / img_width
        y_center = (y_min + height / 2) / img_height
        norm_width = width / img_width
        norm_height = height / img_height
        
        # 记录原始和转换后的坐标信息
        logger.debug(f"原始bbox: x={x_min}, y={y_min}, w={width}, h={height}")
        logger.debug(f"YOLO格式: 类别={class_id}, x_center={x_center}, y_center={y_center}, w={norm_width}, h={norm_height}")
        
        # YOLO格式：class_id x_center y_center width height
        file_handler.write(f"{class_id} {x_center} {y_center} {norm_width} {norm_height}\n")
        return True

    def _compute_bounding_box(self, file_handler, points, img_width, img_height, class_id=0):
        """计算多边形的边界框并输出YOLO格式"""
        try:
            if not points or len(points) < 3:
                logger.error(f"点数量不足以形成多边形: {len(points) if points else 0}个点")
                return False
            
            # 记录多边形点的数量和部分点的坐标，便于调试
            logger.debug(f"处理多边形: {len(points)}个点")
            for i, p in enumerate(points[:3]):  # 只记录前三个点
                logger.debug(f"点{i}: x={p[0]}, y={p[1]}")
            
            # 提取所有x和y坐标
            x_values = []
            y_values = []
            for p in points:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x_values.append(float(p[0]))
                    y_values.append(float(p[1]))
                elif isinstance(p, dict) and 'x' in p and 'y' in p:
                    x_values.append(float(p['x']))
                    y_values.append(float(p['y']))
            
            if not x_values or not y_values:
                logger.error("无法从多边形点中提取有效坐标")
                return False
            
            # 计算边界框坐标
            x_min = min(x_values)
            y_min = min(y_values)
            x_max = max(x_values)
            y_max = max(y_values)
            
            # 计算宽度和高度
            width = x_max - x_min
            height = y_max - y_min
            
            # 检查边界框是否有效
            if width <= 0 or height <= 0:
                logger.error(f"计算得到的边界框无效: width={width}, height={height}")
                return False
            
            # 转换为YOLO格式 (x_center, y_center, width, height)，归一化到[0,1]
            x_center = (x_min + width / 2) / img_width
            y_center = (y_min + height / 2) / img_height
            norm_width = width / img_width
            norm_height = height / img_height
            
            # 记录原始和转换后的坐标信息
            logger.debug(f"多边形边界框: x={x_min}, y={y_min}, w={width}, h={height}")
            logger.debug(f"YOLO格式: 类别={class_id}, x_center={x_center}, y_center={y_center}, w={norm_width}, h={norm_height}")
            
            # YOLO格式：class_id x_center y_center width height
            file_handler.write(f"{class_id} {x_center} {y_center} {norm_width} {norm_height}\n")
            return True
        except Exception as e:
            logger.error(f"计算多边形边界框失败: {str(e)}", exc_info=True)
            return False
            
    def _create_dataset_config(self, dataset: Dataset, dataset_dir: str) -> None:
        """创建YOLO数据集配置文件"""
        # 获取类别名称
        class_names = self._get_class_names()
        
        # 创建dataset.yaml
        yaml_path = os.path.join(dataset_dir, "dataset.yaml")
        with open(yaml_path, 'w') as f:
            f.write(f"path: {os.path.abspath(dataset_dir)}\n")  # 使用绝对路径
            f.write("train: train/images\n")
            f.write("val: val/images\n")
            f.write(f"nc: {len(class_names)}\n")  # 类别数量
            f.write("\n")
            # 输出类别名称列表
            f.write(f"names: {json.dumps(class_names)}\n")
            
        logger.info(f"创建数据集配置，类别数量: {len(class_names)}, 类别: {class_names}")

    def _update_training_status(self, model_id: int, status: ModelStatus, error_message: str = None) -> None:
        """更新模型训练状态"""
        db = None
        try:
            # 创建新的数据库会话
            from sqlalchemy.orm import sessionmaker
            from ..models.base import engine
            
            Session = sessionmaker(engine)
            db = Session()
            
            model = db.query(Model).filter(Model.id == model_id).first()
            if model:
                model.status = status
                model.updated_at = datetime.utcnow()
                
                # 如果有错误信息，添加到指标中
                if error_message:
                    if model.metrics is None:
                        model.metrics = {}
                    model.metrics['error'] = error_message
                    
                db.commit()
                logger.info(f"成功更新模型 {model_id} 状态为 {status}")
            else:
                logger.error(f"找不到模型ID: {model_id}")
        except Exception as e:
            logger.error(f"更新模型训练状态失败: {str(e)}")
            if db:
                try:
                    db.rollback()
                except:
                    pass
        finally:
            if db:
                try:
                    db.close()
                    logger.debug(f"关闭_update_training_status中的数据库会话")
                except:
                    pass

    def export_model(self, model_id: int, export_path: str = None) -> str:
        """导出模型到文件"""
        model = self.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
            
        # 检查模型状态，只有已完成的模型才能导出
        if model.status != ModelStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Model training not completed")
            
        # 如果没有提供导出路径，使用默认路径
        if not export_path:
            export_dir = os.path.join(".", "models", "exports")
            os.makedirs(export_dir, exist_ok=True)
            export_path = os.path.join(export_dir, f"model_{model_id}.pt")
            
        # 如果模型文件存在，复制到导出路径
        if model.file_path and os.path.exists(model.file_path):
            try:
                shutil.copy(model.file_path, export_path)
                logger.info(f"模型已导出到: {export_path}")
                return export_path
            except Exception as e:
                logger.error(f"模型导出失败: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to export model: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Model file not found")
            
    def test_model(self, model_id: int, image_path: str, conf_thres: float = 0.25, iou_thres: float = 0.45):
        """使用指定模型测试图像"""
        # 获取模型实例
        try:
            # 加载图像
            img = cv2.imread(image_path)
            if img is None:
                raise HTTPException(status_code=400, detail="Invalid image file")
            
            # 获取并检查模型
            yolo_model = self.get_model_instance(model_id)
            
            # 应用模型参数
            if hasattr(yolo_model.model, 'conf') and conf_thres is not None:
                yolo_model.model.conf = conf_thres
            
            if hasattr(yolo_model.model, 'iou') and iou_thres is not None:
                yolo_model.model.iou = iou_thres
            
            # 执行预测
            annotated_img, detections = yolo_model.predict(img)
            
            # 记录检测结果
            logger.info(f"模型 {model_id} 检测到 {len(detections)} 个对象")
            for i, det in enumerate(detections):
                logger.info(f"检测 {i+1}: 类别={det['class_name']}, 置信度={det['confidence']:.2f}")
            
            return annotated_img, detections
            
        except Exception as e:
            logger.error(f"模型测试失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Model test failed: {str(e)}")
            
    def test_model_image(self, model_id: int, image: np.ndarray, conf_thres: float = 0.25, iou_thres: float = 0.45):
        """
        使用指定模型测试numpy格式的图像
        
        Args:
            model_id: 模型ID
            image: 图像数据，numpy数组格式
            conf_thres: 置信度阈值
            iou_thres: IOU阈值
            
        Returns:
            annotated_img, detections: 标注后的图像和检测结果
        """
        try:
            # 检查图像是否有效
            if image is None or image.size == 0:
                raise HTTPException(status_code=400, detail="Invalid image data")
            
            # 获取并检查模型
            yolo_model = self.get_model_instance(model_id)
            
            # 应用模型参数
            if hasattr(yolo_model.model, 'conf') and conf_thres is not None:
                yolo_model.model.conf = conf_thres
            
            if hasattr(yolo_model.model, 'iou') and iou_thres is not None:
                yolo_model.model.iou = iou_thres
            
            # 执行预测
            annotated_img, detections = yolo_model.predict(image)
            
            # 记录检测结果
            logger.info(f"模型 {model_id} 检测到 {len(detections)} 个对象")
            for i, det in enumerate(detections):
                logger.info(f"检测 {i+1}: 类别={det['class_name']}, 置信度={det['confidence']:.2f}")
            
            return annotated_img, detections
            
        except Exception as e:
            logger.error(f"模型测试失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Model test failed: {str(e)}")

    # 由于之前的方法可能被其他地方调用，这里保留方法但简化实现
    def _train_yolov8(self, model_id: int, dataset_dir: str) -> None:
        """使用YOLOv8进行训练"""
        model = self.get_model(model_id)
        if model:
            self._run_yolo_training(model_id, dataset_dir, model.parameters, "YOLOv8")

    def _train_yolov5(self, model_id: int, dataset_dir: str) -> None:
        """使用YOLOv5进行训练"""
        model = self.get_model(model_id)
        if model:
            self._run_yolo_training(model_id, dataset_dir, model.parameters, "YOLOv5") 