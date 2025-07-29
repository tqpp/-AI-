from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from pydantic import Field, validator
import base64
import numpy as np
import json
import cv2

from ..routers.base import CamelModel
from ..services.cv_operation import CVOperationService
from ..dependencies import get_db
from ..models import ParamType

router = APIRouter(prefix="/api/cv/operations", tags=["cv_operations"])

# --- 基础模型 ---
class ParamConfigBase(CamelModel):
    """参数配置基础模型"""
    name: str = Field(..., description="参数名称")
    type: str = Field(..., description="参数类型")
    description: Optional[str] = Field(None, description="参数描述")
    default: Optional[Union[str, int, float, bool, dict, list]] = Field(None, description="默认值")
    required: bool = Field(False, description="是否必需")

    @validator('name')
    def validate_name(cls, v):
        if not v.isidentifier():
            raise ValueError("参数名称必须是有效的Python标识符")
        return v

    @validator('type')
    def validate_type(cls, v):
        valid_types = ["text", "number", "boolean", "array", "object", "image"]
        if v not in valid_types:
            raise ValueError(f"参数类型必须是以下之一: {', '.join(valid_types)}")
        return v

    @validator('default')
    def validate_default(cls, v, values):
        if v is None:
            return v
            
        param_type = values.get('type')
        
        # 如果值已经是正确的类型，直接返回
        if param_type == 'text' and isinstance(v, str):
            return v
        elif param_type == 'number' and isinstance(v, (int, float)):
            return v
        elif param_type == 'boolean' and isinstance(v, bool):
            return v
        elif param_type == 'array' and isinstance(v, list):
            return v
        elif param_type == 'object' and isinstance(v, dict):
            return v
        elif param_type == 'image' and isinstance(v, str):
            return v
            
        # 如果值是字符串，尝试转换为正确的类型
        if isinstance(v, str):
            try:
                if param_type == 'number':
                    # 尝试转换为数字
                    if '.' in v:
                        return float(v)
                    else:
                        return int(v)
                elif param_type == 'boolean':
                    # 转换为布尔值
                    return v.lower() in ('true', '1', 'yes', 'y')
                elif param_type == 'array':
                    # 尝试解析JSON数组
                    return json.loads(v)
                elif param_type == 'object':
                    # 尝试解析JSON对象
                    return json.loads(v)
                else:
                    # 文本和图像类型保持字符串
                    return v
            except Exception as e:
                raise ValueError(f"无法将字符串转换为{param_type}类型: {str(e)}")
        
        # 如果不是字符串且类型不匹配，抛出错误
        raise ValueError(f"{param_type}类型参数的默认值必须是{param_type}或字符串")

# --- 响应模型 ---
class CVOperationResponse(CamelModel):
    id: int = Field(..., description="操作ID")
    name: str = Field(..., min_length=1, max_length=100, description="操作名称")
    description: Optional[str] = Field(None, description="操作描述")
    code: str = Field(..., description="操作代码")
    inputParams: List[ParamConfigBase] = Field(default_factory=list, description="输入参数配置")
    outputParams: List[ParamConfigBase] = Field(default_factory=list, description="输出参数配置")
    createdAt: datetime = Field(..., description="创建时间")
    updatedAt: datetime = Field(..., description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "图像预处理",
                "description": "对图像进行预处理操作",
                "code": "def process(image):\n    return cv2.resize(image, (224, 224))",
                "inputParams": [
                    {
                        "name": "image",
                        "type": "object",
                        "description": "输入图像",
                        "required": True
                    }
                ],
                "outputParams": [
                    {
                        "name": "result",
                        "type": "object",
                        "description": "处理后的图像",
                        "required": True
                    }
                ],
                "createdAt": "2024-03-22T10:00:00",
                "updatedAt": "2024-03-22T10:00:00"
            }
        }

class ApplyOperationResponse(CamelModel):
    """应用操作响应模型"""
    result: Dict[str, Union[str, int, float, bool, dict, list]] = Field(..., description="操作结果")

    @validator('result')
    def validate_result(cls, v):
        """确保结果是可序列化的"""
        if not isinstance(v, dict):
            raise ValueError("结果必须是字典类型")
        return v

# --- 请求模型 ---
class CreateOperationRequest(CamelModel):
    name: str = Field(..., min_length=1, max_length=100, description="操作名称")
    description: Optional[str] = Field(None, description="操作描述")
    code: str = Field(..., description="操作代码")
    inputParams: List[ParamConfigBase] = Field(default_factory=list, description="输入参数配置")
    outputParams: List[ParamConfigBase] = Field(default_factory=list, description="输出参数配置")

    @validator('code')
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError("代码不能为空")
        return v.strip()

class UpdateOperationRequest(CamelModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="操作名称")
    description: Optional[str] = Field(None, description="操作描述")
    code: Optional[str] = Field(None, description="操作代码")
    inputParams: Optional[List[ParamConfigBase]] = Field(None, description="输入参数配置")
    outputParams: Optional[List[ParamConfigBase]] = Field(None, description="输出参数配置")

    @validator('code')
    def validate_code(cls, v):
        if v is not None and not v.strip():
            raise ValueError("代码不能为空")
        return v.strip() if v is not None else v

class ApplyOperationRequest(CamelModel):
    inputParams: Dict[str, Any] = Field(..., description="输入参数值")

# --- 路由处理函数 ---
@router.get("/", response_model=List[CVOperationResponse])
async def get_operations(db: Session = Depends(get_db)):
    """获取所有CV操作"""
    service = CVOperationService(db)
    operations = service.get_operations()
    
    return [
        CVOperationResponse(
            id=op.id,
            name=op.name,
            description=op.description,
            code=op.code,
            inputParams=[ParamConfigBase(**param) for param in op.input_params],
            outputParams=[ParamConfigBase(**param) for param in op.output_params],
            createdAt=op.created_at,
            updatedAt=op.updated_at
        )
        for op in operations
    ]

@router.get("/{operation_id}", response_model=CVOperationResponse)
async def get_operation(operation_id: int, db: Session = Depends(get_db)):
    """获取单个CV操作"""
    service = CVOperationService(db)
    operation = service.get_operation(operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    return CVOperationResponse(
        id=operation.id,
        name=operation.name,
        description=operation.description,
        code=operation.code,
        inputParams=[ParamConfigBase(**param) for param in operation.input_params],
        outputParams=[ParamConfigBase(**param) for param in operation.output_params],
        createdAt=operation.created_at,
        updatedAt=operation.updated_at
    )

@router.post("/", response_model=CVOperationResponse)
async def create_operation(
    request: CreateOperationRequest,
    db: Session = Depends(get_db)
):
    """创建新的CV操作"""
    service = CVOperationService(db)
    try:
        # 将 Pydantic 模型转换为字典
        operation_data = {
            "name": request.name,
            "description": request.description,
            "code": request.code,
            "input_params": [param.dict() for param in request.inputParams],
            "output_params": [param.dict() for param in request.outputParams]
        }
        
        # 直接传递字典参数
        operation = service.create_operation(**operation_data)
        return CVOperationResponse(
            id=operation.id,
            name=operation.name,
            description=operation.description,
            code=operation.code,
            inputParams=[ParamConfigBase(**param) for param in operation.input_params],
            outputParams=[ParamConfigBase(**param) for param in operation.output_params],
            createdAt=operation.created_at,
            updatedAt=operation.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create operation: {str(e)}"
        )

@router.put("/{operation_id}", response_model=CVOperationResponse)
async def update_operation(
    operation_id: int,
    request: UpdateOperationRequest,
    db: Session = Depends(get_db)
):
    """更新CV操作"""
    service = CVOperationService(db)
    try:
        # 将 Pydantic 模型转换为字典，只包含非空字段
        update_data = request.dict(exclude_unset=True)
        
        # 处理输入和输出参数
        if "inputParams" in update_data:
            update_data["input_params"] = [
                param if isinstance(param, dict) else param.dict()
                for param in update_data.pop("inputParams")
            ]
        if "outputParams" in update_data:
            update_data["output_params"] = [
                param if isinstance(param, dict) else param.dict()
                for param in update_data.pop("outputParams")
            ]
        
        # 直接传递字典参数
        operation = service.update_operation(operation_id, **update_data)
        return CVOperationResponse(
            id=operation.id,
            name=operation.name,
            description=operation.description,
            code=operation.code,
            inputParams=[ParamConfigBase(**param) for param in operation.input_params],
            outputParams=[ParamConfigBase(**param) for param in operation.output_params],
            createdAt=operation.created_at,
            updatedAt=operation.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update operation: {str(e)}"
        )

@router.delete("/{operation_id}")
async def delete_operation(operation_id: int, db: Session = Depends(get_db)):
    """删除CV操作"""
    service = CVOperationService(db)
    service.delete_operation(operation_id=operation_id)
    return {"status": "success"}

@router.post("/{operation_id}/apply", response_model=ApplyOperationResponse)
async def apply_operation(
    operation_id: int,
    request: ApplyOperationRequest,
    db: Session = Depends(get_db)
):
    """应用CV操作"""
    service = CVOperationService(db)
    try:
        # 获取操作
        operation = service.get_operation(operation_id)
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")

        # 验证和转换输入参数
        processed_params = {}
        for param_config in operation.input_params:
            param_name = param_config['name']
            param_type = param_config['type']
            param_value = request.inputParams.get(param_name)
            
            if param_value is None:
                if param_config.get('required', False):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing required parameter: {param_name}"
                    )
                continue

            try:
                if param_type == 'image':
                    # 验证图片数据
                    if not isinstance(param_value, str):
                        raise ValueError("图片参数必须是base64字符串")
                    try:
                        # 验证base64格式
                        image_data = base64.b64decode(param_value)
                        nparr = np.frombuffer(image_data, np.uint8)
                        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if img is None:
                            raise ValueError("无效的图片数据")
                        processed_params[param_name] = img
                    except Exception as e:
                        raise ValueError(f"图片数据解码失败: {str(e)}")
                        
                elif param_type == 'number':
                    try:
                        processed_params[param_name] = float(param_value)
                    except (ValueError, TypeError):
                        raise ValueError(f"参数 {param_name} 必须是数字")
                        
                elif param_type == 'text':
                    processed_params[param_name] = str(param_value)
                    
                elif param_type == 'boolean':
                    processed_params[param_name] = bool(param_value)
                    
                elif param_type in ('array', 'object'):
                    if isinstance(param_value, str):
                        try:
                            processed_params[param_name] = json.loads(param_value)
                        except json.JSONDecodeError:
                            raise ValueError(f"参数 {param_name} 的JSON格式无效")
                    else:
                        processed_params[param_name] = param_value
                else:
                    processed_params[param_name] = param_value
                    
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"参数 {param_name} 处理失败: {str(e)}"
                )

        # 执行操作
        result = service.apply_operation(operation_id, processed_params)
        
        # 处理输出结果
        output_data = {}
        for param_config in operation.output_params:
            param_name = param_config['name']
            param_type = param_config['type']
            
            if param_name not in result:
                raise ValueError(f"缺少输出参数: {param_name}")
                
            value = result[param_name]
            
            if param_type == 'image':
                # 处理图像输出 - 可能是numpy数组或已经是base64字符串
                if isinstance(value, np.ndarray):
                    # 将numpy数组转换为base64字符串
                    success, encoded_img = cv2.imencode('.png', value)
                    if not success:
                        raise ValueError(f"图像编码失败: {param_name}")
                    output_data[param_name] = base64.b64encode(encoded_img.tobytes()).decode('utf-8')
                elif isinstance(value, str):
                    # 假设已经是base64字符串
                    output_data[param_name] = value
                else:
                    raise ValueError(f"参数 {param_name} 的输出类型错误，应为图像数据或base64字符串")
            else:
                output_data[param_name] = value
                
        return ApplyOperationResponse(result=output_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"操作执行失败: {str(e)}"
        )