import { apiService } from './api'
import { ParamConfig } from './cv_operation'

// 节点类型枚举
export enum NodeType {
  START = 'start',
  END = 'end',
  OPERATION = 'operation',
  PARALLEL = 'parallel',
  MERGE = 'merge',
  CONDITION = 'condition'
}

// 边类型枚举
export enum EdgeType {
  NORMAL = 'normal',
  TRUE = 'true',
  FALSE = 'false'
}

// 节点位置接口
export interface Position {
  x: number
  y: number
}

// 节点配置接口
export interface NodeConfig {
  id: string
  type: NodeType
  name?: string
  operationId?: number
  config?: Record<string, any>
  position: Position
}

// 边配置接口
export interface EdgeConfig {
  id: string
  source: string
  target: string
  type: EdgeType
}

// 流水线元数据接口
export interface PipelineMetadata {
  nodes: NodeConfig[]
  edges: EdgeConfig[]
}

// 流水线接口
export interface Pipeline {
  id: number
  name: string
  description: string | null
  metadata: PipelineMetadata
  inputParams: ParamConfig[]
  outputParams: ParamConfig[]
  createdAt: string
  updatedAt: string
}

// 创建流水线请求接口
export interface CreatePipelineRequest {
  name: string
  description?: string
  metadata: PipelineMetadata
  inputParams: ParamConfig[]
  outputParams: ParamConfig[]
}

// 更新流水线请求接口
export interface UpdatePipelineRequest {
  name?: string
  description?: string
  metadata?: PipelineMetadata
  inputParams?: ParamConfig[]
  outputParams?: ParamConfig[]
}

// 应用流水线请求接口
export interface ApplyPipelineRequest {
  inputParams: Record<string, any>
  enableLog?: boolean
}

// 应用流水线响应接口
export interface ApplyPipelineResponse {
  outputParams: Record<string, any>
  logs: Array<{
    time: string
    type: string
    message: string
  }>
}

export class PipelineService {
  /**
   * 获取所有流水线列表
   */
  async getPipelines(): Promise<Pipeline[]> {
    const response = await apiService.get<Pipeline[]>('/pipelines/')
    return response
  }

  /**
   * 获取单个流水线详情
   */
  async getPipeline(id: number): Promise<Pipeline> {
    const response = await apiService.get<Pipeline>(`/pipelines/${id}`)
    return response
  }

  /**
   * 创建新的流水线
   */
  async createPipeline(data: CreatePipelineRequest): Promise<Pipeline> {
    const response = await apiService.post<Pipeline>('/pipelines/', data)
    return response
  }

  /**
   * 更新流水线
   */
  async updatePipeline(id: number, data: UpdatePipelineRequest): Promise<Pipeline> {
    const response = await apiService.put<Pipeline>(`/pipelines/${id}`, data)
    return response
  }

  /**
   * 删除流水线
   */
  async deletePipeline(id: number): Promise<void> {
    await apiService.delete(`/pipelines/${id}`)
  }

  /**
   * 应用流水线处理
   */
  async applyPipeline(pipelineId: number, data: ApplyPipelineRequest): Promise<ApplyPipelineResponse> {
    const response = await apiService.post<ApplyPipelineResponse>(
      `/pipelines/${pipelineId}/apply`,
      data
    )
    return response
  }

  /**
   * 验证流水线配置
   * @param metadata 流水线元数据
   * @returns 如果验证通过返回true，否则抛出错误
   */
  validatePipelineMetadata(metadata: PipelineMetadata): boolean {
    console.log('metadata', metadata)
    // 验证节点
    const startNodes = metadata.nodes.filter(node => node.type === NodeType.START)
    const endNodes = metadata.nodes.filter(node => node.type === NodeType.END)

    if (startNodes.length !== 1) {
      throw new Error('流水线必须有且仅有一个开始节点')
    }
    if (endNodes.length !== 1) {
      throw new Error('流水线必须有且仅有一个结束节点')
    }

    // 验证节点ID唯一性
    const nodeIds = new Set<string>()
    for (const node of metadata.nodes) {
      if (nodeIds.has(node.id)) {
        throw new Error(`重复的节点ID: ${node.id}`)
      }
      nodeIds.add(node.id)

      // 验证操作节点
      if (node.type === NodeType.OPERATION && !node.operationId) {
        throw new Error(`操作节点 ${node.id} 必须指定操作ID`)
      }
    }

    // 验证边的连接
    for (const edge of metadata.edges) {
      if (!nodeIds.has(edge.source)) {
        throw new Error(`边的源节点不存在: ${edge.source}`)
      }
      if (!nodeIds.has(edge.target)) {
        throw new Error(`边的目标节点不存在: ${edge.target}`)
      }
    }

    // 验证条件节点的分支
    const conditionNodes = metadata.nodes.filter(node => node.type === NodeType.CONDITION)
    for (const node of conditionNodes) {
      const outgoingEdges = metadata.edges.filter(edge => edge.source === node.id)
      const hasTrue = outgoingEdges.some(edge => edge.type === EdgeType.TRUE)
      const hasFalse = outgoingEdges.some(edge => edge.type === EdgeType.FALSE)
      
      if (!hasTrue || !hasFalse) {
        throw new Error(`条件节点 ${node.id} 必须有真分支和假分支`)
      }
    }

    return true
  }
}

export const pipelineService = new PipelineService() 