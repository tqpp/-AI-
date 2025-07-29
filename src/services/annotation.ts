import { apiService } from './api'

// 数据集类型枚举
export enum DatasetType {
  TEXT_REGION = 'text_region',
  OCR = 'ocr'
}

// 数据集
export interface Dataset {
  id: number
  name: string
  type: DatasetType
  imageCount: number
  createdAt: string
  updatedAt: string
}

// 图片
export interface Image {
  id: number
  filename: string
  url: string
  isAnnotated: boolean
  datasetId: number
  createdAt: string
}

// 保存标注请求 - 使用 Annotorious 格式
export interface SaveAnnotationRequest {
  annotations: any[] // 使用 Annotorious 的原生格式
}

// 获取标注响应
export interface GetAnnotationResponse {
  annotations: any[] // 使用 Annotorious 的原生格式
}

// 创建数据集请求
export interface CreateDatasetRequest {
  name: string
  type: DatasetType
}

// 更新数据集请求
export interface UpdateDatasetRequest {
  name: string
}

// 实现服务类
export class AnnotationService {
  // 数据集管理
  async getDatasets(): Promise<Dataset[]> {
    try {
      const response = await apiService.get<Dataset[]>('/annotation/datasets')
      return response
    } catch (error) {
      throw error
    }
  }

  async createDataset(data: CreateDatasetRequest): Promise<Dataset> {
    const response = await apiService.post<Dataset>(
      '/annotation/datasets',
      data
    )
    return response
  }

  async renameDataset(datasetId: number, name: string): Promise<Dataset> {
    try {
      const response = await apiService.put<Dataset>(
        `/annotation/datasets/${datasetId}`,
        { name }
      )
      return response
    } catch (error) {
      console.error('重命名数据集失败:', error)
      throw error
    }
  }

  async deleteDataset(datasetId: number): Promise<void> {
    await apiService.delete<void>(`/annotation/datasets/${datasetId}`)
  }

  // 图片管理
  async getDatasetImages(datasetId: number): Promise<Image[]> {
    const response = await apiService.get<Image[]>(
      `/annotation/datasets/${datasetId}/images`
    )
    return response
  }

  async uploadImages(datasetId: number, files: File[]): Promise<Image[]> {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    const response = await apiService.post<Image[]>(
      `/annotation/datasets/${datasetId}/images`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      } as any
    )
    return response
  }

  async deleteImage(imageId: number): Promise<void> {
    await apiService.delete(`/annotation/images/${imageId}`)
  }

  // 标注管理
  async getImageAnnotation(imageId: number): Promise<GetAnnotationResponse> {
    try {
      const response = await apiService.get<any>(
        `/annotation/images/${imageId}/annotation`
      )
      
      // 如果后端返回的数据包含 annotations 字段，直接返回
      if (response && response.annotations) {
        return {
          annotations: response.annotations
        }
      }
      
      // 否则返回空数组
      return { annotations: [] }
    } catch (error) {
      console.error('Failed to get annotations:', error)
      // 出错时返回空数组
      return { annotations: [] }
    }
  }

  async saveAnnotation(imageId: number, data: SaveAnnotationRequest): Promise<void> {
    try {
      console.log('Saving annotations:', data)
      await apiService.post(
        `/annotation/images/${imageId}/annotation`,
        data
      )
    } catch (error) {
      console.error('Failed to save annotations:', error)
      throw error
    }
  }
}