import { apiService } from './api';

// Enums to match backend
export enum ModelStatus {
  NOT_STARTED = 'not_started',
  TRAINING = 'training',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export enum ModelArchitecture {
  YOLO_V5 = 'yolo_v5',
  YOLO_V8 = 'yolo_v8',
  YOLO_V9 = 'yolo_v9'
}

// Model interfaces
export interface Model {
  id: number;
  name: string;
  architecture: ModelArchitecture;
  dataset_id: number;
  status: ModelStatus;
  parameters: {
    epochs?: number;
    batch_size?: number;
    [key: string]: any;
  };
  metrics?: {
    accuracy?: number;
    loss?: number;
    progress?: number;
    [key: string]: any;
  };
  created_at: string;
  updated_at: string;
  file_path?: string;
}

// Request interfaces
export interface CreateModelRequest {
  name: string;
  architecture: ModelArchitecture;
  dataset_id?: number;
  parameters?: {
    epochs?: number;
    batch_size?: number;
    [key: string]: any;
  };
}

export interface UpdateModelRequest {
  name?: string;
  parameters?: {
    epochs?: number;
    batch_size?: number;
    [key: string]: any;
  };
}

// 文件浏览相关接口
export interface ModelFile {
  name: string;
  path: string;
  isDir: boolean;
  size: number;
  modifiedTime: string;
}

export interface FileListResponse {
  files: ModelFile[];
}

export interface FileContentResponse {
  content: string;
}

export class ModelService {
  /**
   * 获取所有模型列表
   */
  async getModels(): Promise<Model[]> {
    const response = await apiService.get<Model[]>('/models/');
    return response;
  }

  /**
   * 获取特定数据集的所有模型
   */
  async getModelsByDataset(datasetId: number): Promise<Model[]> {
    const response = await apiService.get<Model[]>(`/models?dataset_id=${datasetId}`);
    return response;
  }

  /**
   * 获取单个模型
   */
  async getModel(id: number): Promise<Model> {
    const response = await apiService.get<Model>(`/models/${id}`);
    return response;
  }

  /**
   * 创建新模型
   */
  async createModel(data: CreateModelRequest): Promise<Model> {
    const requestData = {
      name: data.name,
      architecture: data.architecture,
      dataset_id: data.dataset_id,
      parameters: data.parameters
    };
    
    const response = await apiService.post<Model>('/models/', requestData);
    return response;
  }

  /**
   * 更新模型
   */
  async updateModel(id: number, data: UpdateModelRequest): Promise<Model> {
    const requestData: any = {};
    if (data.name !== undefined) requestData.name = data.name;
    if (data.parameters !== undefined) requestData.parameters = data.parameters;
    
    const response = await apiService.put<Model>(`/models/${id}`, requestData);
    return response;
  }

  /**
   * 删除模型
   */
  async deleteModel(id: number): Promise<void> {
    await apiService.delete(`/models/${id}`);
  }

  /**
   * 开始训练模型
   */
  async startTraining(id: number): Promise<Model> {
    const response = await apiService.post<Model>(`/models/${id}/train`);
    return response;
  }

  /**
   * 导出模型
   */
  async exportModel(id: number): Promise<{ message: string; file_path: string }> {
    const response = await apiService.get<{ message: string; file_path: string }>(`/models/${id}/export`);
    return response;
  }

  /**
   * 获取模型训练日志
   */
  async getModelLogs(id: number): Promise<{
    model_id: number;
    logs: string[];
  }> {
    const response = await apiService.get<{
      model_id: number;
      logs: string[];
    }>(`/models/${id}/logs`);
    return response;
  }

  /**
   * 测试模型
   */
  async testModel(id: number, imageFile: File, params?: { conf_thres?: number; iou_thres?: number }): Promise<{
    success: boolean;
    detections?: any[];
    image?: string;
    error?: string;
  }> {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    if (params?.conf_thres !== undefined) {
      formData.append('conf_thres', params.conf_thres.toString());
    }
    
    if (params?.iou_thres !== undefined) {
      formData.append('iou_thres', params.iou_thres.toString());
    }
    
    try {
      const response = await apiService.post<{
        success: boolean;
        detections?: any[];
        image?: string;
        error?: string;
      }>(`/models/${id}/test`, formData);
      return response;
    } catch (error: any) {
      return {
        success: false,
        error: error.message || '测试模型失败'
      };
    }
  }

  /**
   * 测试模型 (使用base64编码的图像)
   */
  async testModelWithBase64(id: number, imageBase64: string, params?: { conf_thres?: number; iou_thres?: number }): Promise<{
    success: boolean;
    detections?: any[];
    image?: string;
    error?: string;
  }> {
    try {
      const requestData = {
        image_base64: imageBase64,
        conf_thres: params?.conf_thres ?? 0.25,
        iou_thres: params?.iou_thres ?? 0.45
      };
      
      const response = await apiService.post<{
        success: boolean;
        detections?: any[];
        image?: string;
        error?: string;
      }>(`/models/${id}/test`, requestData);
      
      return response;
    } catch (error: any) {
      return {
        success: false,
        error: error.message || '测试模型失败'
      };
    }
  }

  /**
   * 获取模型文件列表
   */
  async getModelFiles(id: number, path: string = ''): Promise<FileListResponse> {
    const response = await apiService.get<FileListResponse>(`/models/${id}/files?path=${encodeURIComponent(path)}`);
    return response;
  }

  /**
   * 获取文件内容（文本文件）
   */
  async getFileContent(modelId: number, path: string): Promise<FileContentResponse> {
    const response = await apiService.get<FileContentResponse>(`/models/${modelId}/files/content?path=${encodeURIComponent(path)}`);
    return response;
  }

  /**
   * 获取文件预览链接（图片文件）
   */
  getFilePreviewUrl(modelId: number, path: string): string {
    return `${apiService.getBaseUrl()}/models/${modelId}/files/preview?path=${encodeURIComponent(path)}`;
  }

  /**
   * 获取文件下载链接
   */
  getFileDownloadUrl(modelId: number, path: string): string {
    return `${apiService.getBaseUrl()}/models/${modelId}/files/download?path=${encodeURIComponent(path)}`;
  }

  /**
   * 测试模型（使用base64图像）
   */
  async testModelBase64(modelId: number, imageBase64: string, confThres?: number, iouThres?: number): Promise<any> {
    const payload = {
      image_base64: imageBase64,
      conf_thres: confThres,
      iou_thres: iouThres
    };
    
    const response = await apiService.post<any>(`/models/${modelId}/test`, payload);
    return response;
  }
}

export const modelService = new ModelService();