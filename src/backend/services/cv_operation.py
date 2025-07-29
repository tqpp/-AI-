import base64
import json
import cv2
from fastapi.datastructures import FormData
import numpy as np
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from ..models import CVOperation, ParamType, ParamConfig
from datetime import datetime
from typing import List, Optional, Dict, Any
from .model import ModelService

class CVOperationService:
    def __init__(self, db: Session):
        self.db = db
        self.model_service = ModelService(db)
        
        # 初始化代码执行上下文
        self.context = {
            'cv2': cv2,
            'np': np,
            'get_yolo_model': self._get_yolo_model,  # 添加获取YOLO模型的函数
            'get_all_models': self._get_all_models    # 添加获取所有已加载模型的函数
        }

    def _get_yolo_model(self, model_id: int):
        """
        获取YOLO模型实例，供CV操作使用
        
        在操作中的调用示例:
        ```python
        def process(image, **params):
            # 获取YOLO模型
            yolo_model = get_yolo_model(1)  # 传入模型ID
            
            # 使用模型预测
            annotated_img, detections = yolo_model.predict(image)
            
            return {
                'output_image': annotated_img,
                'detections': detections
            }
        ```
        """
        try:
            return self.model_service.get_model_instance(model_id)
        except Exception as e:
            raise ValueError(f"获取YOLO模型失败: {str(e)}")
            
    def _get_all_models(self):
        """
        获取所有已加载的模型字典，供CV操作使用
        
        在操作中的调用示例:
        ```python
        def process(image, **params):
            # 获取所有已加载模型
            models = get_all_models()
            
            # 获取模型ID列表
            model_ids = list(models.keys())
            
            # 使用某个模型进行预测
            if model_ids:
                yolo_model = models[model_ids[0]]
                annotated_img, detections = yolo_model.predict(image)
                return {
                    'output_image': annotated_img,
                    'detections': detections
                }
            else:
                return {
                    'output_image': image,
                    'error': '没有可用的模型'
                }
        ```
        
        Returns:
            Dict[int, YOLOModel]: 模型ID到模型实例的映射字典
        """
        try:
            return self.model_service._loaded_models
        except Exception as e:
            raise ValueError(f"获取已加载模型失败: {str(e)}")

    def get_operations(self) -> List[CVOperation]:
        """获取所有CV操作"""
        return self.db.query(CVOperation).all()

    def get_operation(self, operation_id: int) -> Optional[CVOperation]:
        """获取指定CV操作"""
        return self.db.query(CVOperation).filter(CVOperation.id == operation_id).first()

    def create_operation(self, name: str, code: str, 
                        input_params: List[ParamConfig] = None,
                        output_params: List[ParamConfig] = None,
                        description: str = None) -> CVOperation:
        """创建新的CV操作"""
        try:
            operation = CVOperation(
                name=name,
                description=description,
                code=code,
                input_params=input_params or [],
                output_params=output_params or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(operation)
            self.db.commit()
            self.db.refresh(operation)
            return operation
        except Exception as e:
            self.db.rollback()
            raise e

    def update_operation(self, operation_id: int, name: str = None, 
                        code: str = None, description: str = None,
                        input_params: List[ParamConfig] = None,
                        output_params: List[ParamConfig] = None) -> CVOperation:
        """更新CV操作"""
        operation = self.get_operation(operation_id)
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")

        if name is not None:
            operation.name = name
        if code is not None:
            operation.code = code
        if description is not None:
            operation.description = description
        if input_params is not None:
            operation.input_params = input_params
        if output_params is not None:
            operation.output_params = output_params
            
        operation.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(operation)
            return operation
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_operation(self, operation_id: int) -> None:
        """删除CV操作"""
        operation = self.get_operation(operation_id)
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")
            
        try:
            self.db.delete(operation)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e 
        
    def apply_operation(self, operation_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """应用CV操作并返回处理结果"""
        operation = self.get_operation(operation_id)
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")

        try:
            # 创建完整的参数字典，确保所有定义的参数都存在
            complete_params = {}
            
            # 为每个定义的输入参数创建条目，如果参数未提供则使用默认值
            for param_config in operation.input_params:
                param_name = param_config['name']
                param_type = param_config['type']
                param_default = param_config.get('default')
                
                # 如果参数未提供，使用默认值
                if param_name not in params:
                    complete_params[param_name] = param_default
                    continue
                
                # 获取参数值并进行类型处理
                param_value = params.get(param_name)
                
                # 如果参数值为None且有默认值，使用默认值
                if param_value is None and param_default is not None:
                    param_value = param_default
                
                # 根据参数类型处理
                if param_type == 'image':
                    # 处理图像参数
                    if isinstance(param_value, str):
                        try:
                            # 如果是base64字符串，转换为numpy数组
                            image_data = base64.b64decode(param_value)
                            nparr = np.frombuffer(image_data, np.uint8)
                            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            if img is None:
                                raise ValueError(f"无效的图像数据: {param_name}")
                            complete_params[param_name] = img
                        except Exception as e:
                            raise HTTPException(
                                status_code=400,
                                detail=f"无法解码图像参数 {param_name}: {str(e)}"
                            )
                    elif isinstance(param_value, np.ndarray):
                        # 直接使用numpy数组
                        complete_params[param_name] = param_value
                    elif param_value is None:
                        # 保持None值
                        complete_params[param_name] = None
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail=f"图像参数 {param_name} 类型不正确，期望numpy.ndarray或base64字符串，但得到 {type(param_value)}"
                        )
                elif param_type == 'number':
                    # 处理数字参数
                    try:
                        if param_value is not None:
                            complete_params[param_name] = float(param_value)
                        else:
                            complete_params[param_name] = None
                    except (ValueError, TypeError):
                        raise HTTPException(
                            status_code=400,
                            detail=f"无法将参数 {param_name} 转换为数字类型"
                        )
                elif param_type == 'boolean':
                    # 处理布尔参数
                    if param_value is not None:
                        complete_params[param_name] = bool(param_value)
                    else:
                        complete_params[param_name] = None
                elif param_type == 'text':
                    # 处理文本参数
                    if param_value is not None:
                        complete_params[param_name] = str(param_value)
                    else:
                        complete_params[param_name] = None
                elif param_type == 'array':
                    # 处理数组参数
                    if param_value is None:
                        complete_params[param_name] = None
                    elif isinstance(param_value, list):
                        complete_params[param_name] = param_value
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail=f"参数 {param_name} 类型不正确，期望数组类型，但得到 {type(param_value)}"
                        )
                elif param_type == 'object':
                    # 处理对象参数
                    if param_value is None:
                        complete_params[param_name] = None
                    elif isinstance(param_value, dict):
                        complete_params[param_name] = param_value
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail=f"参数 {param_name} 类型不正确，期望对象类型，但得到 {type(param_value)}"
                        )
                else:
                    # 其他类型直接传递
                    complete_params[param_name] = param_value
            
            # 准备执行环境
            exec_context = {
                **self.context,
                **complete_params
            }

            # 执行代码
            namespace = {}
            try:
                exec(operation.code, exec_context, namespace)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"执行操作代码出错: {str(e)}"
                )

            if 'process' not in namespace:
                raise HTTPException(
                    status_code=400,
                    detail="操作代码中未定义'process'函数"
                )

            # 验证处理函数
            process_func = namespace['process']
            if not callable(process_func):
                raise HTTPException(
                    status_code=400,
                    detail="'process'必须是一个可调用的函数"
                )

            # 执行处理函数，确保传入所有定义的参数
            try:
                result = process_func(**complete_params)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"执行process函数时出错: {str(e)}"
                )

            # 验证输出
            if not operation.output_params:
                raise HTTPException(
                    status_code=400,
                    detail="未配置输出类型"
                )

            # 验证输出参数
            output_data = {}
            for param_config in operation.output_params:
                param_name = param_config['name']
                param_type = param_config['type']
                
                if not isinstance(result, dict):
                    raise HTTPException(
                        status_code=400,
                        detail=f"process函数必须返回字典类型，但返回了 {type(result)}"
                    )
                
                if param_name not in result:
                    raise HTTPException(
                        status_code=400,
                        detail=f"缺少输出参数: {param_name}"
                    )
                
                # 对于图像类型的输出，保持numpy数组格式
                if param_type == 'image' and isinstance(result[param_name], np.ndarray):
                    output_data[param_name] = result[param_name]
                else:
                    output_data[param_name] = result[param_name]

            return output_data
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"服务器内部错误: {str(e)}"
            )