from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON, Enum, Boolean, Column, Text, UniqueConstraint, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import Base, engine
from typing import Any, List, Dict, Optional
from typing_extensions import TypedDict

class DatasetType(PyEnum):
    TEXT_REGION = 'text_region'  # 文本区域数据集
    OCR = 'ocr'                  # OCR数据集

class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[DatasetType] = mapped_column(Enum(DatasetType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    images = relationship("Image", back_populates="dataset", cascade="all, delete-orphan")

class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("datasets.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_annotated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dataset = relationship("Dataset", back_populates="images")
    annotation = relationship("Annotation", back_populates="image", cascade="all, delete-orphan")

class Annotation(Base):
    __tablename__ = "annotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images.id"))
    data: Mapped[dict] = mapped_column(JSON, nullable=False)  # 存储标注数据的JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    image = relationship("Image", back_populates="annotation")

class ParamType(PyEnum):
    IMAGE = 'image'           # 图像类型
    NUMBER = 'number'         # 数值类型(int/float)
    TEXT = 'text'            # 文本类型
    BOOLEAN = 'boolean'      # 布尔类型
    ARRAY = 'array'          # 数组类型
    OBJECT = 'object'        # 对象类型

class ParamConfig(TypedDict):
    name: str                # 参数名称
    type: ParamType         # 参数类型
    description: str        # 参数描述
    default: Any           # 默认值
    required: bool         # 是否必需

class NodeType(PyEnum):
    START = 'start'         # 开始节点
    END = 'end'            # 结束节点
    OPERATION = 'operation' # 处理节点
    PARALLEL = 'parallel'  # 并行节点
    MERGE = 'merge'       # 聚合节点
    CONDITION = 'condition' # 条件节点

class EdgeType(PyEnum):
    NORMAL = 'normal'  # 普通连接
    TRUE = 'true'     # 条件为真的分支
    FALSE = 'false'   # 条件为假的分支

class Pipeline(Base):
    """流水线模型"""
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    pipeline_metadata = Column(JSON, nullable=False, default={})  # 存储节点和边的配置
    input_params = Column(JSON, nullable=False, default=[])  # 输入参数配置
    output_params = Column(JSON, nullable=False, default=[])  # 输出参数配置
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)

class CVOperation(Base):
    __tablename__ = "cv_operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    input_params: Mapped[list[ParamConfig]] = mapped_column(JSON, nullable=False, default=list)  # 输入参数配置
    output_params: Mapped[list[ParamConfig]] = mapped_column(JSON, nullable=False, default=list)  # 输入参数配置
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

class ModelStatus(PyEnum):
    NOT_STARTED = 'not_started'
    TRAINING = 'training'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
class ModelArchitecture(PyEnum):
    YOLO_V5 = 'yolo_v5'
    YOLO_V8 = 'yolo_v8'
    YOLO_V9 = 'yolo_v9'

class Model(Base):
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    architecture: Mapped[ModelArchitecture] = mapped_column(Enum(ModelArchitecture), nullable=False)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("datasets.id"))
    status: Mapped[ModelStatus] = mapped_column(Enum(ModelStatus), default=ModelStatus.NOT_STARTED)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    dataset = relationship("Dataset")

# Add this new class for system settings
class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('category', 'key', name='uq_settings_category_key'),
    )

# Add this class for device settings
class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # camera, light, plc
    model: Mapped[str] = mapped_column(String(100), nullable=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="offline")  # online, offline, error
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

# 检测结果状态枚举
class DetectionStatus(PyEnum):
    PASS = 'pass'           # 合格
    FAIL = 'fail'           # 不合格
    UNKNOWN = 'unknown'     # 未知

# 历史检测记录模型
class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    text: Mapped[str] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[DetectionStatus] = mapped_column(Enum(DetectionStatus), nullable=False, default=DetectionStatus.UNKNOWN)
    image_path: Mapped[str] = mapped_column(String(1000), nullable=True)
    processed_image_path: Mapped[str] = mapped_column(String(1000), nullable=True)
    operation_id: Mapped[int] = mapped_column(Integer, nullable=True)  # 关联的操作ID(可能是cv_operation或pipeline)
    operation_type: Mapped[str] = mapped_column(String(50), nullable=True)  # operation或pipeline
    detection_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)  # 额外的检测元数据
    
    # 关联到设备
    device = relationship("Device", foreign_keys=[device_id])

# 告警类型枚举
class AlertType(PyEnum):
    ERROR = 'error'         # 错误
    WARNING = 'warning'     # 警告
    INFO = 'info'           # 信息

# 系统告警模型
class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False, default=AlertType.INFO)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id"), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    
    # 关联到设备
    device = relationship("Device", foreign_keys=[device_id])

Base.metadata.create_all(bind=engine)