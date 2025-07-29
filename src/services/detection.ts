import { apiService } from './api';

export interface Detection {
  id: number;
  text: string | null;
  confidence: number | null;
  status: string;
  deviceId?: number;
  deviceName?: string;
  timestamp: string;
  imagePath?: string;
  processedImagePath?: string;
  operationId?: number;
  operationType?: string;
  metadata?: Record<string, any>;
}

export interface PaginatedDetections {
  items: Detection[];
  total: number;
  page: number;
  perPage: number;
  pages: number;
}

export interface DetectionFilter {
  page?: number;
  perPage?: number;
  searchText?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
  deviceId?: number;
  confidenceMin?: number;
  confidenceMax?: number;
}

export interface DetectionCreate {
  text?: string;
  confidence?: number;
  status?: string;
  deviceId?: number;
  imageData?: string;
  processedImageData?: string;
  operationId?: number;
  operationType?: string;
  metadata?: Record<string, any>;
}

export class DetectionService {
  /**
   * 获取分页的检测记录列表
   */
  async getDetections(filters: DetectionFilter = {}): Promise<PaginatedDetections> {
    let url = '/detections';
    
    // 添加查询参数
    const queryParams = new URLSearchParams();
    
    if (filters.page) queryParams.append('page', filters.page.toString());
    if (filters.perPage) queryParams.append('per_page', filters.perPage.toString());
    if (filters.searchText) queryParams.append('search_text', filters.searchText);
    if (filters.status) queryParams.append('status', filters.status);
    
    // 确保日期格式是YYYY-MM-DD
    if (filters.dateFrom) {
      const dateFrom = filters.dateFrom.replace(/\//g, '-');
      queryParams.append('date_from', dateFrom);
      console.log('发送日期范围[从]:', dateFrom);
    }
    
    if (filters.dateTo) {
      const dateTo = filters.dateTo.replace(/\//g, '-');
      queryParams.append('date_to', dateTo);
      console.log('发送日期范围[到]:', dateTo);
    }
    
    if (filters.deviceId) queryParams.append('device_id', filters.deviceId.toString());
    if (filters.confidenceMin !== undefined) queryParams.append('confidence_min', filters.confidenceMin.toString());
    if (filters.confidenceMax !== undefined) queryParams.append('confidence_max', filters.confidenceMax.toString());
    
    const queryString = queryParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
    
    return apiService.get<PaginatedDetections>(url);
  }
  
  /**
   * 获取单个检测记录详情
   */
  async getDetection(id: number): Promise<Detection> {
    return apiService.get<Detection>(`/detections/${id}`);
  }
  
  /**
   * 创建新的检测记录
   */
  async createDetection(detection: DetectionCreate): Promise<Detection> {
    return apiService.post<Detection>('/detections', detection);
  }
  
  /**
   * 删除检测记录
   */
  async deleteDetection(id: number): Promise<{ message: string }> {
    return apiService.delete<{ message: string }>(`/detections/${id}`);
  }
  
  /**
   * 清除满足条件的检测记录
   */
  async clearDetections(
    beforeDate?: string,
    status?: string,
    deviceId?: number
  ): Promise<{ message: string }> {
    let url = '/detections';
    
    // 添加查询参数
    const queryParams = new URLSearchParams();
    
    if (beforeDate) {
      // 确保日期格式是YYYY-MM-DD
      const formattedDate = beforeDate.replace(/\//g, '-');
      queryParams.append('before_date', formattedDate);
    }
    
    if (status) queryParams.append('status', status);
    if (deviceId) queryParams.append('device_id', deviceId.toString());
    
    const queryString = queryParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
    
    return apiService.delete<{ message: string }>(url);
  }
  
  /**
   * 保存一个实时检测结果到历史记录
   */
  async saveDetectionResult(
    result: {
      text: string;
      confidence: number;
      passed: boolean;
      imageData: string;
      processedImageData?: string;
      deviceId?: number;
      operationId?: number;
      operationType?: string;
    }
  ): Promise<Detection> {
    const detection: DetectionCreate = {
      text: result.text,
      confidence: result.confidence,
      status: result.passed ? 'pass' : 'fail',
      deviceId: result.deviceId,
      imageData: result.imageData,
      processedImageData: result.processedImageData,
      operationId: result.operationId,
      operationType: result.operationType
    };
    
    return this.createDetection(detection);
  }
}

export const detectionService = new DetectionService(); 