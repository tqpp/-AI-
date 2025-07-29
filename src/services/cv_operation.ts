import { apiService } from './api'

// 参数类型枚举
export enum ParamType {
  IMAGE = 'image',
  NUMBER = 'number',
  TEXT = 'text',
  BOOLEAN = 'boolean',
  ARRAY = 'array',
  OBJECT = 'object'
}

// 参数配置接口
export interface ParamConfig {
  name: string
  type: ParamType
  description: string
  default: any
  required: boolean
}

// CV 操作相关类型
export interface CVOperation {
  id: number
  name: string
  description: string | null
  code: string
  inputParams: ParamConfig[]
  outputParams: ParamConfig[]
  createdAt: string
  updatedAt: string
}

// CV 操作请求类型
export interface CreateCVOperationRequest {
  name: string
  code: string
  description?: string
  inputParams: ParamConfig[]
  outputParams: ParamConfig[]
}

export interface UpdateCVOperationRequest {
  name?: string
  code?: string
  description?: string
  inputParams?: ParamConfig[]
  outputParams?: ParamConfig[]
}

// 应用操作请求类型
export interface ApplyOperationRequest {
  inputParams: Record<string, any>
}

export class CVOperationService {
  /**
   * 获取所有CV操作列表
   */
  async getOperations(): Promise<CVOperation[]> {
    const response = await apiService.get<CVOperation[]>('/cv/operations/')
    return response
  }

  /**
   * 获取单个CV操作详情
   */
  async getOperation(id: number): Promise<CVOperation> {
    const response = await apiService.get<CVOperation>(`/cv/operations/${id}`)
    return response
  }

  /**
   * 创建新的CV操作
   */
  async createOperation(data: CreateCVOperationRequest): Promise<CVOperation> {
    const response = await apiService.post<CVOperation>('/cv/operations/', data)
    return response
  }

  /**
   * 更新CV操作
   */
  async updateOperation(id: number, data: UpdateCVOperationRequest): Promise<CVOperation> {
    const response = await apiService.put<CVOperation>(`/cv/operations/${id}`, data)
    return response
  }

  /**
   * 删除CV操作
   */
  async deleteOperation(id: number): Promise<void> {
    await apiService.delete(`/cv/operations/${id}`)
  }

  /**
   * 应用CV操作处理图像
   */
  async applyOperation(operationId: number, data: ApplyOperationRequest): Promise<any> {
    const response = await apiService.post<any>(
      `/cv/operations/${operationId}/apply`,
      data
    )
    return response.result
  }
}

export const cvOperationService = new CVOperationService() 