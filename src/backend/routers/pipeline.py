from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import Field, validator
import base64
import numpy as np
import cv2

from ..routers.base import CamelModel
from ..services.pipeline import PipelineService
from ..dependencies import get_db
from ..models import NodeType, EdgeType, ParamType, Pipeline
from .cv_operation import ParamConfigBase
from datetime import datetime

router = APIRouter(prefix="/api/pipelines", tags=["pipelines"])

# --- 基础模型 ---
class NodeConfig(CamelModel):
    """节点配置模型"""
    id: str = Field(..., description="节点ID")
    type: str = Field(..., description="节点类型")
    name: Optional[str] = Field(None, description="节点名称")
    operation_id: Optional[int] = Field(None, description="操作ID（仅处理节点需要）")
    config: Optional[Dict[str, Any]] = Field(None, description="节点配置")
    position: Dict[str, float] = Field(..., description="节点位置")

    @validator('type')
    def validate_type(cls, v):
        if v not in [t.value for t in NodeType]:
            raise ValueError(f"无效的节点类型: {v}")
        return v

class EdgeConfig(CamelModel):
    """边配置模型"""
    id: str = Field(..., description="边ID")
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    type: str = Field(EdgeType.NORMAL.value, description="边类型")

    @validator('type')
    def validate_type(cls, v):
        if v not in [t.value for t in EdgeType]:
            raise ValueError(f"无效的边类型: {v}")
        return v

class PipelineMetadata(CamelModel):
    """流水线元数据模型"""
    nodes: List[NodeConfig] = Field(..., description="节点列表")
    edges: List[EdgeConfig] = Field(..., description="边列表")

# --- 响应模型 ---
class PipelineResponse(CamelModel):
    """流水线响应模型"""
    id: int = Field(..., description="流水线ID")
    name: str = Field(..., description="流水线名称")
    description: Optional[str] = Field(None, description="流水线描述")
    metadata: PipelineMetadata = Field(..., description="流水线配置")
    inputParams: List[ParamConfigBase] = Field(default_factory=list, description="输入参数配置")
    outputParams: List[ParamConfigBase] = Field(default_factory=list, description="输出参数配置")
    createdAt: datetime = Field(..., description="创建时间")
    updatedAt: datetime = Field(..., description="更新时间")

    @classmethod
    def from_orm(cls, pipeline: Pipeline):
        return cls(
            id=pipeline.id,
            name=pipeline.name,
            description=pipeline.description,
            metadata=PipelineMetadata(**pipeline.pipeline_metadata),
            inputParams=[ParamConfigBase(**param) for param in pipeline.input_params],
            outputParams=[ParamConfigBase(**param) for param in pipeline.output_params],
            createdAt=pipeline.created_at,
            updatedAt=pipeline.updated_at
        )

# --- 请求模型 ---
class CreatePipelineRequest(CamelModel):
    """创建流水线请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="流水线名称")
    description: Optional[str] = Field(None, description="流水线描述")
    metadata: PipelineMetadata = Field(..., description="流水线配置")
    inputParams: List[ParamConfigBase] = Field(default_factory=list, description="输入参数配置")
    outputParams: List[ParamConfigBase] = Field(default_factory=list, description="输出参数配置")

class UpdatePipelineRequest(CamelModel):
    """更新流水线请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="流水线名称")
    description: Optional[str] = Field(None, description="流水线描述")
    metadata: Optional[PipelineMetadata] = Field(None, description="流水线配置")
    inputParams: Optional[List[ParamConfigBase]] = Field(None, description="输入参数配置")
    outputParams: Optional[List[ParamConfigBase]] = Field(None, description="输出参数配置")

class ApplyPipelineRequest(CamelModel):
    """应用流水线请求模型"""
    inputParams: Dict[str, Any] = Field(..., description="输入参数")
    enableLog: Optional[bool] = Field(False, description="是否启用详细日志")

class ApplyPipelineResponse(CamelModel):
    """应用流水线响应模型"""
    outputParams: Dict[str, Any] = Field(..., description="输出参数")
    logs: List[Dict[str, Any]] = Field(..., description="日志")

# --- 路由处理函数 ---
@router.get("/", response_model=List[PipelineResponse])
async def get_pipelines(db: Session = Depends(get_db)):
    """获取所有流水线"""
    service = PipelineService(db)
    pipelines = service.get_pipelines()
    return [PipelineResponse.from_orm(p) for p in pipelines]

@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    """获取单个流水线"""
    service = PipelineService(db)
    pipeline = service.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return PipelineResponse.from_orm(pipeline)

@router.post("/", response_model=PipelineResponse)
async def create_pipeline(request: CreatePipelineRequest, db: Session = Depends(get_db)):
    """创建新的流水线"""
    service = PipelineService(db)
    try:
        pipeline = service.create_pipeline(
            name=request.name,
            description=request.description,
            metadata=request.metadata.dict(),
            input_params=[param.dict() for param in request.inputParams],
            output_params=[param.dict() for param in request.outputParams]
        )
        return PipelineResponse.from_orm(pipeline)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: int,
    request: UpdatePipelineRequest,
    db: Session = Depends(get_db)
):
    """更新流水线"""
    service = PipelineService(db)
    try:
        # 将请求数据转换为字典，只包含非空字段
        update_data = request.dict(exclude_unset=True)
        
        # 处理metadata和参数
        if "metadata" in update_data:
            update_data["metadata"] = update_data["metadata"]
        if "inputParams" in update_data:
            update_data["input_params"] = [param for param in update_data["inputParams"]]
        if "outputParams" in update_data:
            update_data["output_params"] = [param for param in update_data["outputParams"]]
        
        pipeline = service.update_pipeline(pipeline_id, **update_data)
        return PipelineResponse.from_orm(pipeline)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{pipeline_id}")
async def delete_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    """删除流水线"""
    service = PipelineService(db)
    try:
        service.delete_pipeline(pipeline_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{pipeline_id}/apply", response_model=ApplyPipelineResponse)
async def apply_pipeline(
    pipeline_id: int,
    request: ApplyPipelineRequest,
    db: Session = Depends(get_db)
):
    """应用流水线处理"""
    service = PipelineService(db)
    
    try:
        # 获取流水线
        pipeline = service.get_pipeline(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")

        # 验证并转换输入参数
        processed_params = {}
        for param_config in pipeline.input_params:
            param_name = param_config["name"]
            param_type = param_config["type"]
            
            # 检查必需参数
            if param_config.get("required", False) and param_name not in request.inputParams:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required parameter: {param_name}"
                )
            
            # 如果参数存在，进行类型转换
            if param_name in request.inputParams:
                value = request.inputParams[param_name]
                
                try:
                    # 根据参数类型进行转换
                    if param_type == ParamType.IMAGE.value:
                        # 如果是base64字符串，解码为图像
                        if isinstance(value, str):
                            try:
                                # 移除base64前缀
                                if ',' in value:
                                    value = value.split(',')[1]
                                # 解码base64
                                img_data = base64.b64decode(value)
                                nparr = np.frombuffer(img_data, np.uint8)
                                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                if img is None:
                                    raise ValueError("Invalid image data")
                                processed_params[param_name] = img
                            except Exception as e:
                                raise HTTPException(
                                    status_code=400,
                                    detail=f"Invalid base64 image for parameter {param_name}: {str(e)}"
                                )
                        else:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Image parameter {param_name} must be a base64 string"
                            )
                    
                    elif param_type == ParamType.NUMBER.value:
                        # 转换为数值
                        try:
                            processed_params[param_name] = float(value)
                        except (TypeError, ValueError):
                            raise HTTPException(
                                status_code=400,
                                detail=f"Invalid number value for parameter {param_name}"
                            )
                    
                    elif param_type == ParamType.BOOLEAN.value:
                        # 转换为布尔值
                        if isinstance(value, bool):
                            processed_params[param_name] = value
                        elif isinstance(value, str):
                            processed_params[param_name] = value.lower() in ('true', '1', 'yes')
                        else:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Invalid boolean value for parameter {param_name}"
                            )
                    
                    else:
                        # 其他类型直接使用原值
                        processed_params[param_name] = value
                
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error processing parameter {param_name}: {str(e)}"
                    )

        # 执行流水线，传递 enableLog 参数
        result = service.apply_pipeline(pipeline_id, processed_params, enable_log=request.enableLog)

        # 处理输出结果
        output_params = {}
        for param_config in pipeline.output_params:
            param_name = param_config["name"]
            param_type = param_config["type"]
            
            if param_name in result["outputParams"]:
                value = result["outputParams"][param_name]
                
                # 根据参数类型处理输出
                if param_type == ParamType.IMAGE.value and isinstance(value, np.ndarray):
                    # 将图像转换为base64
                    success, buffer = cv2.imencode('.png', value)
                    if not success:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to encode output image {param_name}"
                        )
                    output_params[param_name] = base64.b64encode(buffer).decode('utf-8')
                else:
                    output_params[param_name] = value

        # 如果启用了日志，则返回日志，否则返回空列表
        logs = result.get('logs', []) if request.enableLog else []
        
        return ApplyPipelineResponse(outputParams=output_params, logs=logs)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 