from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import Pipeline, CVOperation, NodeType, EdgeType
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, Set
import cv2
import numpy as np
from ..services.cv_operation import CVOperationService
import logging
import base64
import json
import signal

# 创建日志记录器
logger = logging.getLogger(__name__)

class NodeResult:
    def __init__(self, 
                 node_type: NodeType,
                 success: bool = True,
                 result: Any = None,
                 error: str = None,
                 operation_id: int = None,
                 operation_name: str = None,
                 output_type: str = None):
        self.node_type = node_type
        self.success = success
        self.result = result
        self.error = error
        self.operation_id = operation_id
        self.operation_name = operation_name
        self.output_type = output_type

    def to_dict(self) -> dict:
        return {
            'type': self.node_type.value,
            'success': self.success,
            'result': self.result,
            'error': self.error,
            'operation_id': self.operation_id,
            'operation_name': self.operation_name,
            'output_type': self.output_type
        }

class PipelineService:
    def __init__(self, db: Session):
        self.db = db
        self.cv_operation_service = CVOperationService(db)
        self.logs = []

    def get_pipelines(self) -> List[Pipeline]:
        """获取所有管道"""
        return self.db.query(Pipeline).all()

    def get_pipeline(self, pipeline_id: int) -> Optional[Pipeline]:
        """获取指定管道"""
        return self.db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    def create_pipeline(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        input_params: Optional[List[Dict[str, Any]]] = None,
        output_params: Optional[List[Dict[str, Any]]] = None
    ) -> Pipeline:
        """创建新的流水线"""
        try:
            # 验证流水线配置
            self._validate_pipeline_metadata(metadata)
            
            pipeline = Pipeline(
                name=name,
                description=description,
                pipeline_metadata=metadata or {},
                input_params=input_params or [],
                output_params=output_params or [],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.db.add(pipeline)
            self.db.commit()
            self.db.refresh(pipeline)
            return pipeline
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def update_pipeline(
        self,
        pipeline_id: int,
        **kwargs
    ) -> Pipeline:
        """更新流水线"""
        try:
            pipeline = self.get_pipeline(pipeline_id)
            if not pipeline:
                raise HTTPException(status_code=404, detail="Pipeline not found")

            # 如果更新了metadata，需要验证
            if "metadata" in kwargs:
                self._validate_pipeline_metadata(kwargs["metadata"])
                kwargs["pipeline_metadata"] = kwargs.pop("metadata")

            # 更新字段
            for key, value in kwargs.items():
                setattr(pipeline, key, value)
            
            pipeline.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(pipeline)
            return pipeline
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def delete_pipeline(self, pipeline_id: int) -> None:
        """删除管道"""
        try:
            pipeline = self.get_pipeline(pipeline_id)
            if not pipeline:
                raise HTTPException(status_code=404, detail="Pipeline not found")
            
            self.db.delete(pipeline)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def _execute_operation(self, operation: CVOperation, img: np.ndarray) -> dict:
        """执行单个操作"""
        try:
            namespace = {}
            exec(operation.code, namespace)
            result = namespace['process'](img, cv2, np)

            return {
                'operation_id': operation.id,
                'operation_name': operation.name,
                'output_type': operation.output_type,
                'result': result,
                'success': True
            }
        except Exception as e:
            return {
                'operation_id': operation.id,
                'operation_name': operation.name,
                'output_type': operation.output_type,
                'error': str(e),
                'success': False
            }

    def _process_node(self, node_id: str, nodes: Dict[str, Any], 
                     edges: List[Dict[str, str]], operations: Dict[int, CVOperation], 
                     results: Dict[str, NodeResult], img: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """处理单个节点，返回(是否继续执行, 输出图像)"""
        node = nodes[node_id]
        node_type = NodeType(node.get('type', NodeType.OPERATION.value))
        
        # 处理开始节点
        if node_type == NodeType.START:
            results[node_id] = NodeResult(
                node_type=NodeType.START,
                output_type='image',
                result=img
            )
            return True, img
        
        # 处理结束节点
        if node_type == NodeType.END:
            results[node_id] = NodeResult(node_type=NodeType.END)
            return True, img

        # 处理条件节点
        if node_type == NodeType.CONDITION:
            condition_result = self._evaluate_condition(node, results)
            results[node_id] = NodeResult(
                node_type=NodeType.CONDITION,
                result=condition_result
            )
            return condition_result, img

        # 处理合并节点
        if node_type == NodeType.MERGE:
            input_edges = [edge for edge in edges if edge['target'] == node_id]
            input_results = [results[edge['source']] for edge in input_edges]
            
            # 合并结果
            merged_result = self._merge_results(input_results)
            results[node_id] = NodeResult(
                node_type=NodeType.MERGE,
                result=merged_result
            )
            return True, img

        # 处理操作节点
        operation_id = node.get('operation_id')
        if operation_id:
            operation = operations.get(operation_id)
            if not operation:
                raise HTTPException(status_code=404, detail=f"Operation {operation_id} not found")

            # 执行操作
            try:
                namespace = {}
                exec(operation.code, namespace)
                result = namespace['process'](img, cv2, np)

                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    operation_id=operation.id,
                    operation_name=operation.name,
                    output_type=operation.output_type,
                    result=result
                )
                
                return True, result if operation.output_type == 'image' else img
                
            except Exception as e:
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    success=False,
                    error=str(e),
                    operation_id=operation.id,
                    operation_name=operation.name,
                    output_type=operation.output_type
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Error in operation {operation.name}: {str(e)}"
                )

        return True, img

    def _evaluate_condition(self, node: Dict[str, Any], results: Dict[str, NodeResult]) -> bool:
        """评估条件节点"""
        try:
            condition = node.get('condition', {})
            condition_type = condition.get('type')
            
            if condition_type == 'compare':
                value = condition.get('value')
                operator = condition.get('operator', '==')
                source_node = condition.get('source_node')
                
                if source_node and source_node in results:
                    source_result = results[source_node].result
                    
                    try:
                        if operator == '==':
                            return source_result == value
                        elif operator == '!=':
                            return source_result != value
                        elif operator == '>':
                            return float(source_result) > float(value)
                        elif operator == '<':
                            return float(source_result) < float(value)
                        elif operator == '>=':
                            return float(source_result) >= float(value)
                        elif operator == '<=':
                            return float(source_result) <= float(value)
                    except (ValueError, TypeError) as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid comparison: {str(e)}"
                        )
            
            elif condition_type == 'and':
                conditions = condition.get('conditions', [])
                return all(self._evaluate_condition({'condition': c}, results) for c in conditions)
            
            elif condition_type == 'or':
                conditions = condition.get('conditions', [])
                return any(self._evaluate_condition({'condition': c}, results) for c in conditions)
            
            elif condition_type == 'not':
                subcondition = condition.get('condition', {})
                return not self._evaluate_condition({'condition': subcondition}, results)
                    
            return False
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error evaluating condition: {str(e)}")

    def _merge_results(self, results: List[NodeResult]) -> Any:
        """合并多个节点的结果"""
        # 如果只有一个结果，直接返回
        if len(results) == 1:
            return results[0].result
        
        # 如果有图像结果，优先返回最后一个图像
        image_results = [r for r in results if r.output_type == 'image']
        if image_results:
            return image_results[-1].result
        
        # 否则返回所有结果的列表
        return [r.result for r in results]

    def apply_pipeline(self, pipeline_id: int, input_params: Dict[str, Any], enable_log: bool = False, timeout: int = 30) -> Dict[str, Any]:
        """执行流水线处理"""
        # 重置日志列表
        self.logs = []
        try:
            # 获取流水线定义
            pipeline = self.get_pipeline(pipeline_id)
            if not pipeline:
                raise ValueError(f"未找到流水线: {pipeline_id}")
            
            # 确保input_params不为None
            if input_params is None:
                input_params = {}
                
            # 安全地记录输入参数 - 避免直接记录可能导致的错误
            safe_params = {}
            for k, v in input_params.items():
                if isinstance(v, np.ndarray):
                    safe_params[k] = f"<numpy.ndarray shape={v.shape}>"
                else:
                    try:
                        safe_params[k] = str(v)[:100]  # 限制长度
                    except:
                        safe_params[k] = "<无法转换为字符串的对象>"
            
            logger.info(f"流水线 {pipeline_id} 的输入参数: {safe_params}")
            
            # 验证输入参数
            self._validate_input_params(pipeline, input_params)
            
            # 执行流水线处理
            if enable_log:
                result = self._execute_pipeline_with_logs(pipeline, input_params, self.logs, enable_log)
            else:
                result = self._execute_pipeline(pipeline, input_params)
            
            # 构建输出
            output_params = {}
            for output_param in pipeline.output_params:
                param_name = output_param['name']
                param_type = output_param['type']
                
                if param_name not in result:
                    raise ValueError(f"流水线执行未生成输出参数: {param_name}")
                
                # 对于图像类型的输出，保持为numpy数组格式
                if param_type == 'image' and isinstance(result[param_name], np.ndarray):
                    # 保留numpy数组，不转换为base64
                    output_params[param_name] = result[param_name]
                else:
                    output_params[param_name] = result[param_name]
            
            return {
                'outputParams': output_params,
                'logs': self.logs if enable_log else None
            }
            
        except Exception as e:
            error_msg = f"流水线执行错误: {str(e)}"
            logger.error(error_msg)
            if enable_log:
                self._add_log(self.logs, "ERROR", error_msg)
            raise

    def _execute_pipeline_with_logs(self, pipeline: Pipeline, input_params: Dict[str, Any], 
                                   logs: List[Dict[str, Any]], enable_log: bool = False) -> Dict[str, Any]:
        """带日志记录的流水线执行"""
        # 获取节点和边
        nodes = {node["id"]: node for node in pipeline.pipeline_metadata["nodes"]}
        edges = pipeline.pipeline_metadata["edges"]
        
        # 获取所有操作
        operation_ids = [node.get("operation_id") for node in nodes.values() 
                        if node.get("type") == NodeType.OPERATION.value and node.get("operation_id")]
        operations = {op.id: op for op in self.db.query(CVOperation).filter(CVOperation.id.in_(operation_ids)).all()}
        
        # 初始化结果存储
        node_results = {}
        
        # 找到开始节点和结束节点
        start_node = next((node for node in nodes.values() if node["type"] == NodeType.START.value), None)
        end_node = next((node for node in nodes.values() if node["type"] == NodeType.END.value), None)
        
        if not start_node:
            if enable_log:
                self._add_log(logs, "ERROR", "流水线缺少开始节点")
            raise ValueError("Pipeline is missing START node")
            
        if not end_node:
            if enable_log:
                self._add_log(logs, "ERROR", "流水线缺少结束节点")
            raise ValueError("Pipeline is missing END node")
        
        # 从开始节点执行流水线
        if enable_log:
            self._add_log(logs, "INFO", "开始执行节点链")
        
        self._execute_node_chain_with_logs(start_node["id"], nodes, edges, operations, node_results, input_params, logs, enable_log)
        
        # 处理结束节点的输出映射
        if enable_log:
            self._add_log(logs, "INFO", "处理输出映射")
        
        output = {}
        
        if end_node.get("config") and end_node["config"].get("outputMappings"):
            output_mappings = end_node["config"]["outputMappings"]
            
            # 遍历流水线定义的输出参数
            for param in pipeline.output_params:
                param_name = param["name"]
                
                # 检查是否有映射
                if param_name in output_mappings:
                    mapping = output_mappings[param_name]
                    
                    # 解析映射值 (格式: "node:nodeId:outputName")
                    if mapping and mapping.startswith("node:"):
                        parts = mapping.split(":")
                        if len(parts) == 3:
                            source_node_id = parts[1]
                            output_name = parts[2]
                            
                            # 获取源节点结果
                            if source_node_id in node_results:
                                node_result = node_results[source_node_id]
                                
                                # 如果是操作节点，尝试获取特定输出
                                if node_result.node_type == NodeType.OPERATION:
                                    if hasattr(node_result.result, "__getitem__") and isinstance(node_result.result, dict):
                                        output[param_name] = node_result.result.get(output_name, None)
                                    else:
                                        # 如果结果不是字典，直接使用整个结果
                                        output[param_name] = node_result.result
                                else:
                                    # 对于非操作节点，直接使用结果
                                    output[param_name] = node_result.result
                
                # 如果没有映射或映射失败，使用默认值
                if param_name not in output:
                    output[param_name] = param.get("default")
        
        # 验证输出参数
        self._validate_output_params(pipeline, output)
        
        return output
    
    def _execute_node_chain_with_logs(self, node_id: str, nodes: Dict[str, Any], edges: List[Dict[str, Any]], 
                                     operations: Dict[int, CVOperation], results: Dict[str, NodeResult], 
                                     input_params: Dict[str, Any], logs: List[Dict[str, Any]], enable_log: bool = False) -> None:
        """带日志记录的节点链执行"""
        # 如果节点已经执行过，直接返回
        if node_id in results:
            return
        
        # 检查节点是否存在
        if node_id not in nodes:
            if enable_log:
                self._add_log(logs, "ERROR", f"节点 {node_id} 不存在")
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found in pipeline")
        
        node = nodes[node_id]
        node_type = NodeType(node.get("type", NodeType.OPERATION.value))
        node_name = node.get("name", f"未命名节点 ({node_id})")
        
        if enable_log:
            self._add_log(logs, "INFO", f"执行节点: {node_name} (类型: {node_type.value})")
        
        # 处理不同类型的节点
        if node_type == NodeType.START:
            # 开始节点，初始化输入
            if enable_log:
                self._add_log(logs, "INFO", "处理开始节点")
            results[node_id] = NodeResult(
                node_type=NodeType.START,
                result=input_params
            )
            
        elif node_type == NodeType.END:
            # 结束节点，收集前置节点结果
            if enable_log:
                self._add_log(logs, "INFO", "处理结束节点")
            incoming_edges = [edge for edge in edges if edge["target"] == node_id]
            
            if not incoming_edges:
                if enable_log:
                    self._add_log(logs, "WARNING", "结束节点没有输入连接")
            
            # 执行所有前置节点
            for edge in incoming_edges:
                source_node_id = edge["source"]
                self._execute_node_chain_with_logs(source_node_id, nodes, edges, operations, results, input_params, logs, enable_log)
            
            # 结束节点不需要处理结果
            results[node_id] = NodeResult(
                node_type=NodeType.END
            )
            
        elif node_type == NodeType.OPERATION:
            # 操作节点，执行操作
            operation_id = node.get("operation_id")
            
            # 增强错误处理
            if not operation_id:
                # 记录错误但继续执行
                if enable_log:
                    error_msg = f"操作节点 {node_name} 没有指定操作ID"
                    self._add_log(logs, "ERROR", error_msg)
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    success=False,
                    error=error_msg
                )
                return
            
            # 尝试转换操作ID为整数
            try:
                operation_id = int(operation_id)
            except (ValueError, TypeError):
                # 记录错误但继续执行
                if enable_log:
                    error_msg = f"节点 {node_name} 的操作ID格式无效: {operation_id}"
                    self._add_log(logs, "ERROR", error_msg)
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    success=False,
                    error=error_msg
                )
                return
            
            # 检查操作是否存在
            if operation_id not in operations:
                # 尝试从数据库重新获取操作
                operation = self.db.query(CVOperation).filter(CVOperation.id == operation_id).first()
                if not operation:
                    # 记录错误但继续执行
                    if enable_log:
                        error_msg = f"找不到节点 {node_name} 引用的操作 {operation_id}"
                        self._add_log(logs, "ERROR", error_msg)
                    results[node_id] = NodeResult(
                        node_type=NodeType.OPERATION,
                        success=False,
                        error=error_msg
                    )
                    return
                
                # 将操作添加到缓存
                operations[operation_id] = operation
            
            # 获取操作
            operation = operations[operation_id]
            if enable_log:
                self._add_log(logs, "INFO", f"执行操作: {operation.name}")
            
            # 解析参数
            try:
                params = self._resolve_node_params(node, nodes, results, input_params)
                if enable_log:
                    self._add_log(logs, "INFO", f"操作参数解析完成: {list(params.keys())}")
            except Exception as e:
                error_msg = f"解析节点 {node_name} 的参数时出错: {str(e)}"
                if enable_log:
                    self._add_log(logs, "ERROR", error_msg)
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    success=False,
                    error=error_msg
                )
                return
            
            # 使用 cv_operation_service 执行操作
            try:
                # 调用 apply_operation 方法
                if enable_log:
                    self._add_log(logs, "INFO", f"开始执行操作代码")
                result = self.cv_operation_service.apply_operation(operation_id, params)
                if enable_log:
                    self._add_log(logs, "SUCCESS", f"操作执行成功，输出: {list(result.keys()) if isinstance(result, dict) else '非字典结果'}")
                
                # 如果结果包含图像，记录图像信息并转换为base64
                if enable_log and isinstance(result, dict):
                    for key, value in result.items():
                        if isinstance(value, np.ndarray):
                            shape_str = f"{value.shape[0]}x{value.shape[1]}" if len(value.shape) >= 2 else str(value.shape)
                            self._add_log(logs, "INFO", f"输出包含图像: {key} ({shape_str})")
                            
                            # 将图像转换为base64以便在日志中显示
                            try:
                                success, buffer = cv2.imencode('.png', value)
                                if success:
                                    base64_img = base64.b64encode(buffer).decode('utf-8')
                                    self._add_log(logs, "IMAGE", base64_img)
                            except Exception as e:
                                self._add_log(logs, "WARNING", f"无法将图像转换为base64: {str(e)}")
                        else:
                            # 记录非图像输出
                            value_str = str(value)
                            if len(value_str) > 100:
                                value_str = value_str[:100] + "..."
                            self._add_log(logs, "INFO", f"输出参数 {key}: {value_str}")
                
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    operation_id=operation.id,
                    operation_name=operation.name,
                    result=result
                )
            except Exception as e:
                # 记录错误但继续执行
                error_msg = f"执行操作 {operation.name} 时出错: {str(e)}"
                if enable_log:
                    self._add_log(logs, "ERROR", error_msg)
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    success=False,
                    error=error_msg,
                    operation_id=operation.id,
                    operation_name=operation.name
                )
                return
                
        elif node_type == NodeType.CONDITION:
            # 条件节点，评估条件
            if enable_log:
                self._add_log(logs, "INFO", f"评估条件节点")
            condition = node.get("config", {}).get("condition", "True")
            
            try:
                # 解析参数
                params = self._resolve_node_params(node, nodes, results, input_params)
                if enable_log:
                    self._add_log(logs, "INFO", f"条件参数解析完成: {list(params.keys())}")
                
                # 评估条件
                if enable_log:
                    self._add_log(logs, "INFO", f"条件表达式: {condition}")
                condition_result = eval(condition, {"__builtins__": {}}, {"input": params})
                condition_result = bool(condition_result)
                if enable_log:
                    self._add_log(logs, "INFO", f"条件评估结果: {condition_result}")
                
                results[node_id] = NodeResult(
                    node_type=NodeType.CONDITION,
                    result=condition_result
                )
                
                # 根据条件结果选择下一个节点
                outgoing_edges = [edge for edge in edges if edge["source"] == node_id]
                for edge in outgoing_edges:
                    edge_type = edge.get("type", "NORMAL")
                    if (edge_type == "TRUE" and condition_result) or \
                       (edge_type == "FALSE" and not condition_result) or \
                       edge_type == "NORMAL":
                        if enable_log:
                            self._add_log(logs, "INFO", f"条件分支: 选择 {edge_type} 路径")
                        self._execute_node_chain_with_logs(edge["target"], nodes, edges, operations, results, input_params, logs, enable_log)
            except Exception as e:
                error_msg = f"评估条件节点 {node_name} 时出错: {str(e)}"
                if enable_log:
                    self._add_log(logs, "ERROR", error_msg)
                results[node_id] = NodeResult(
                    node_type=NodeType.CONDITION,
                    success=False,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Error evaluating condition in node {node_id}: {str(e)}"
                )
        
        # 处理后续节点
        if node_type != NodeType.CONDITION:  # 条件节点已经在上面处理了后续节点
            outgoing_edges = [edge for edge in edges if edge["source"] == node_id]
            for edge in outgoing_edges:
                self._execute_node_chain_with_logs(edge["target"], nodes, edges, operations, results, input_params, logs, enable_log)
    
    def _add_log(self, logs: List[Dict[str, Any]], log_type: str, message: str) -> None:
        """添加日志条目"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        logs.append({
            "time": timestamp,
            "type": log_type,
            "message": message
        })
        # 同时输出到服务器日志
        log_level = getattr(logging, log_type.upper() if hasattr(logging, log_type.upper()) else "INFO")
        logger.log(log_level, f"[Pipeline] {message}")

    def _validate_pipeline_metadata(self, metadata: Dict[str, Any]) -> None:
        """验证管道配置的有效性"""
        if not metadata:
            raise HTTPException(status_code=400, detail="Pipeline metadata is required")

        nodes = metadata.get("nodes", [])
        edges = metadata.get("edges", [])

        if not nodes:
            raise HTTPException(status_code=400, detail="Pipeline must have at least one node")

        # 验证节点
        node_ids = set()
        start_nodes = []
        end_nodes = []

        for node in nodes:
            # 验证必需字段
            if not all(k in node for k in ["id", "type"]):
                raise HTTPException(status_code=400, detail="Node must have id and type")

            # 验证节点ID唯一性
            if node["id"] in node_ids:
                raise HTTPException(status_code=400, detail=f"Duplicate node id: {node['id']}")
            node_ids.add(node["id"])

            # 统计开始和结束节点
            if node["type"] == NodeType.START.value:
                start_nodes.append(node)
            elif node["type"] == NodeType.END.value:
                end_nodes.append(node)

            # 验证操作节点
            if node["type"] == NodeType.OPERATION.value and not node.get("operation_id"):
                raise HTTPException(status_code=400, detail=f"Operation node {node['id']} must have operation_id")

        # 验证开始和结束节点
        if len(start_nodes) != 1:
            raise HTTPException(status_code=400, detail="Pipeline must have exactly one start node")
        if len(end_nodes) != 1:
            raise HTTPException(status_code=400, detail="Pipeline must have exactly one end node")

        # 验证边
        for edge in edges:
            # 验证必需字段
            if not all(k in edge for k in ["id", "source", "target"]):
                raise HTTPException(status_code=400, detail="Edge must have id, source and target")

            # 验证源节点和目标节点存在
            if edge["source"] not in node_ids:
                raise HTTPException(status_code=400, detail=f"Source node not found: {edge['source']}")
            if edge["target"] not in node_ids:
                raise HTTPException(status_code=400, detail=f"Target node not found: {edge['target']}")

        # 验证图的连通性
        self._validate_graph_connectivity(nodes, edges)

    def _validate_graph_connectivity(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> None:
        """验证图的连通性"""
        # 找到开始节点
        start_node = next(node for node in nodes if node["type"] == NodeType.START.value)
        
        # 使用DFS验证从开始节点是否可以到达所有节点
        visited = set()
        self._dfs(start_node["id"], edges, visited)

        # 检查是否访问了所有节点
        if len(visited) != len(nodes):
            raise HTTPException(status_code=400, detail="Pipeline graph is not fully connected")

    def _dfs(self, node_id: str, edges: List[Dict[str, Any]], visited: Set[str]) -> None:
        """深度优先搜索"""
        visited.add(node_id)
        for edge in edges:
            if edge["source"] == node_id and edge["target"] not in visited:
                self._dfs(edge["target"], edges, visited)

    def _validate_input_params(self, pipeline: Pipeline, input_params: Dict[str, Any]) -> None:
        """验证输入参数"""
        required_params = {param["name"] for param in pipeline.input_params}
        provided_params = set(input_params.keys())

        # 检查是否提供了所有必需参数
        missing_params = required_params - provided_params
        if missing_params:
            raise HTTPException(status_code=400, detail=f"Missing required parameters: {missing_params}")

        # 检查参数类型
        for param in pipeline.input_params:
            if param["name"] in input_params:
                # TODO: 实现参数类型验证
                pass

    def _validate_output_params(self, pipeline: Pipeline, output: Dict[str, Any]) -> None:
        """验证输出参数"""
        required_params = {param["name"] for param in pipeline.output_params}
        provided_params = set(output.keys())

        # 检查是否提供了所有必需参数
        missing_params = required_params - provided_params
        if missing_params:
            raise HTTPException(status_code=400, detail=f"Missing required output parameters: {missing_params}")

        # 检查参数类型
        for param in pipeline.output_params:
            if param["name"] in output:
                # TODO: 实现参数类型验证
                pass

    def _execute_pipeline(self, pipeline: Pipeline, input_params: Dict[str, Any]) -> Dict[str, Any]:
        """执行流水线处理"""
        # 获取节点和边
        nodes = {node["id"]: node for node in pipeline.pipeline_metadata["nodes"]}
        edges = pipeline.pipeline_metadata["edges"]

        # 获取所有操作
        operation_ids = [node.get("operation_id") for node in nodes.values() 
                        if node.get("type") == NodeType.OPERATION.value and node.get("operation_id")]
        operations = {op.id: op for op in self.db.query(CVOperation).filter(CVOperation.id.in_(operation_ids)).all()}
        
        # 初始化结果存储
        node_results = {}
        
        # 找到开始节点和结束节点
        start_node = next(node for node in nodes.values() if node["type"] == NodeType.START.value)
        end_node = next(node for node in nodes.values() if node["type"] == NodeType.END.value)
        
        # 从开始节点执行流水线
        self._execute_node_chain(start_node["id"], nodes, edges, operations, node_results, input_params)
        
        # 处理结束节点的输出映射
        output = {}
        if end_node.get("config") and end_node["config"].get("outputMappings"):
            output_mappings = end_node["config"]["outputMappings"]
            
            # 遍历流水线定义的输出参数
            for param in pipeline.output_params:
                param_name = param["name"]
                
                # 检查是否有映射
                if param_name in output_mappings:
                    mapping = output_mappings[param_name]
                    
                    # 解析映射值 (格式: "node:nodeId:outputName")
                    if mapping and mapping.startswith("node:"):
                        parts = mapping.split(":")
                        if len(parts) == 3:
                            source_node_id = parts[1]
                            output_name = parts[2]
                            
                            # 获取源节点结果
                            if source_node_id in node_results:
                                node_result = node_results[source_node_id]
                                
                                # 如果是操作节点，尝试获取特定输出
                                if node_result.node_type == NodeType.OPERATION:
                                    if hasattr(node_result.result, "__getitem__") and isinstance(node_result.result, dict):
                                        output[param_name] = node_result.result.get(output_name, None)
                                    else:
                                        # 如果结果不是字典，直接使用整个结果
                                        output[param_name] = node_result.result
                                else:
                                    # 对于非操作节点，直接使用结果
                                    output[param_name] = node_result.result
                
                # 如果没有映射或映射失败，使用默认值
                if param_name not in output:
                    output[param_name] = param.get("default")
        
        # 验证输出参数
        self._validate_output_params(pipeline, output)
        
        return output

    def _execute_node_chain(self, node_id: str, nodes: Dict[str, Any], edges: List[Dict[str, Any]], 
                           operations: Dict[int, CVOperation], results: Dict[str, NodeResult], 
                           input_params: Dict[str, Any]) -> None:
        """执行节点链"""
        # 如果节点已经执行过，直接返回
        if node_id in results:
            return
        
        # 检查节点是否存在
        if node_id not in nodes:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found in pipeline")
        
        node = nodes[node_id]
        node_type = NodeType(node.get("type", NodeType.OPERATION.value))
        
        # 处理不同类型的节点
        if node_type == NodeType.START:
            # 开始节点，初始化输入
            results[node_id] = NodeResult(
                node_type=NodeType.START,
                result=input_params
            )
        elif node_type == NodeType.END:
            # 结束节点，收集前置节点结果
            incoming_edges = [edge for edge in edges if edge["target"] == node_id]
            for edge in incoming_edges:
                source_id = edge["source"]
                self._execute_node_chain(source_id, nodes, edges, operations, results, input_params)
            
            results[node_id] = NodeResult(
                node_type=NodeType.END,
                result=None  # 结束节点不需要结果，输出映射在外部处理
            )
        elif node_type == NodeType.OPERATION:
            # 操作节点，执行操作
            operation_id = node.get("operation_id")
            
            # 增强错误处理
            if not operation_id:
                # 记录错误但继续执行
                print(f"Warning: Operation node {node_id} has no operation_id")
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    success=False,
                    error=f"No operation ID specified for node {node_id}"
                )
                return
            
            # 尝试转换操作ID为整数
            try:
                operation_id = int(operation_id)
            except (ValueError, TypeError):
                # 记录错误但继续执行
                print(f"Warning: Invalid operation ID format for node {node_id}: {operation_id}")
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    success=False,
                    error=f"Invalid operation ID format: {operation_id}"
                )
                return
            
            # 检查操作是否存在
            if operation_id not in operations:
                # 尝试从数据库重新获取操作
                operation = self.db.query(CVOperation).filter(CVOperation.id == operation_id).first()
                if not operation:
                    # 记录错误但继续执行
                    print(f"Warning: Operation {operation_id} not found for node {node_id}")
                    results[node_id] = NodeResult(
                        node_type=NodeType.OPERATION,
                        success=False,
                        error=f"Operation {operation_id} not found"
                    )
                    return
                
                # 将操作添加到缓存
                operations[operation_id] = operation
            
            # 获取操作
            operation = operations[operation_id]
            
            # 获取参数值
            params = self._resolve_node_params(node, nodes, results, input_params)
            
            # 使用 cv_operation_service 执行操作
            try:
                # 调用 apply_operation 方法
                result = self.cv_operation_service.apply_operation(operation_id, params)
                
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    operation_id=operation.id,
                    operation_name=operation.name,
                    result=result
                )
            except Exception as e:
                # 记录错误但继续执行
                print(f"Error executing operation {operation.name} for node {node_id}: {str(e)}")
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    success=False,
                    error=str(e),
                    operation_id=operation.id,
                    operation_name=operation.name
                )
        elif node_type == NodeType.CONDITION:
            # 条件节点，评估条件
            condition = node.get("config", {}).get("condition", "True")
            params = self._resolve_node_params(node, nodes, results, input_params)
            
            try:
                # 评估条件
                condition_result = eval(condition, {"__builtins__": {}}, {"input": params})
                condition_result = bool(condition_result)
                
                results[node_id] = NodeResult(
                    node_type=NodeType.CONDITION,
                    result=condition_result
                )
                
                # 根据条件结果选择下一个节点
                outgoing_edges = [edge for edge in edges if edge["source"] == node_id]
                for edge in outgoing_edges:
                    edge_type = edge.get("type", "NORMAL")
                    if (edge_type == "TRUE" and condition_result) or \
                       (edge_type == "FALSE" and not condition_result) or \
                       edge_type == "NORMAL":
                        self._execute_node_chain(edge["target"], nodes, edges, operations, results, input_params)
            except Exception as e:
                results[node_id] = NodeResult(
                    node_type=NodeType.CONDITION,
                    success=False,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Error evaluating condition in node {node_id}: {str(e)}"
                )
        
        # 处理后续节点
        if node_type != NodeType.CONDITION:  # 条件节点已经在上面处理了后续节点
            outgoing_edges = [edge for edge in edges if edge["source"] == node_id]
            for edge in outgoing_edges:
                self._execute_node_chain(edge["target"], nodes, edges, operations, results, input_params)

    def _resolve_node_params(self, node: Dict, nodes: Dict, results: Dict[str, NodeResult], input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析节点的参数值
        
        Args:
            node: 节点定义
            nodes: 所有节点定义
            results: 节点执行结果
            input_params: 流水线输入参数
            
        Returns:
            解析后的参数字典
        """
        resolved_params = {}
        
        # 检查节点是否有config.params属性
        if not node:
            logger.warning("节点对象为空")
            return resolved_params
            
        if not node.get("config"):
            logger.warning(f"节点没有config属性: {node.get('id', 'unknown')}")
            return resolved_params
            
        params_dict = node["config"].get("params")
        if not params_dict:
            logger.warning(f"节点没有config.params属性: {node.get('id', 'unknown')}")
            return resolved_params
            
        if not isinstance(params_dict, dict):
            logger.warning(f"节点参数配置不是字典类型: {node.get('id', 'unknown')}")
            return resolved_params
        
        # 处理每个参数
        for param_name, param_config in params_dict.items():
            try:
                # 检查参数配置是否是字典
                if not isinstance(param_config, dict):
                    logger.warning(f"参数配置无效: {param_name} = {param_config}")
                    continue
                
                # 解析参数来源和值
                param_source = param_config.get("source")
                param_value = param_config.get("value")
                
                # 如果有source属性且格式为"input:参数名"，使用输入参数
                if param_source and isinstance(param_source, str) and param_source.startswith("input:"):
                    input_param_name = param_source.split(":", 1)[1]
                    if input_params and input_param_name in input_params:
                        resolved_params[param_name] = input_params[input_param_name]
                    else:
                        # 更安全的处理方式：记录警告并使用默认值
                        logger.warning(f"未找到输入参数: {input_param_name}，将使用原始值")
                        resolved_params[param_name] = param_value
                # 如果有source属性且格式为"node:节点ID:参数名"，使用其他节点的输出
                elif param_source and isinstance(param_source, str) and param_source.startswith("node:"):
                    parts = param_source.split(":", 2)
                    if len(parts) == 3:
                        source_node_id = parts[1]
                        source_param_name = parts[2]
                        
                        if results and source_node_id in results:
                            node_result = results[source_node_id]
                            if not node_result.success:
                                logger.warning(f"引用的节点执行失败: {source_node_id}，将使用原始值")
                                resolved_params[param_name] = param_value
                            else:
                                if node_result.node_type == NodeType.OPERATION:
                                    if node_result.result is not None and hasattr(node_result.result, "__getitem__") and isinstance(node_result.result, dict):
                                        if source_param_name in node_result.result:
                                            resolved_params[param_name] = node_result.result[source_param_name]
                                        else:
                                            logger.warning(f"未找到引用的参数: {source_param_name}，将使用原始值")
                                            resolved_params[param_name] = param_value
                                    else:
                                        # 如果结果不是字典，直接使用整个结果
                                        resolved_params[param_name] = node_result.result
                                else:
                                    # 对于非操作节点，直接使用结果
                                    resolved_params[param_name] = node_result.result
                        else:
                            logger.warning(f"未找到引用的节点: {source_node_id}，将使用原始值")
                            resolved_params[param_name] = param_value
                # 处理自定义参数
                elif param_source and isinstance(param_source, str) and param_source == "custom":
                    resolved_params[param_name] = param_value
                else:
                    # 使用参数值（如果存在）
                    resolved_params[param_name] = param_value
            except Exception as e:
                logger.error(f"解析参数 {param_name} 时出错: {str(e)}")
                resolved_params[param_name] = param_value
                
        # 图像参数特殊处理：确保图像为空时不会引发错误
        if "img" in resolved_params and (resolved_params["img"] is None or 
                                    (isinstance(resolved_params["img"], np.ndarray) and resolved_params["img"].size == 0)):
            logger.warning(f"节点 {node.get('id', 'unknown')} 的图像参数为空")
            # 创建一个小的空白图像，以避免cvtColor等操作失败
            resolved_params["img"] = np.zeros((10, 10, 3), dtype=np.uint8)
        
        return resolved_params 