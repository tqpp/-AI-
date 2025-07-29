import { apiService } from './api';
import { Device } from './settings';

export interface CameraService {
  getCameraStreamUrl(cameraId: string, options?: StreamOptions): string;
  getCameraIdFromDevice(device: Device): string | null;
  getCameraStatus(cameraId: string): Promise<{ status: string; message: string; clients?: number }>;
  get apiBase(): string;
}

export interface DetectedCamera {
  device_id: number;
  name: string;
  type: string;
  model: string;
  status: string;
  config: {
    resolution: string;
    fps: number;
    format: string;
    source: string;
    [key: string]: any;
  };
}

export interface StreamOptions {
  operation_id?: number;
  operation_type?: 'operation' | 'pipeline';
}

export class CameraServiceImpl implements CameraService {
  get apiBase(): string {
    return apiService.getBaseUrl() || '';
  }

  async getCameraStatus(cameraId: string): Promise<{ status: string; message: string; clients?: number }> {
    return apiService.get<{ status: string; message: string; clients?: number }>(`/cameras/${cameraId}/status`);
  }

  /**
   * 获取摄像头流URL
   * @param cameraId 摄像头ID
   * @param options 可选的流选项（操作ID和类型）
   * @returns 流URL
   */
  getCameraStreamUrl(cameraId: string, options?: StreamOptions): string {
    // 规范化摄像头ID
    if (!cameraId.startsWith('camera_') && !isNaN(Number(cameraId))) {
      cameraId = `camera_${cameraId}`;
    }
    
    // 确保有apiBase，如果没有则使用相对路径
    const base = this.apiBase || '/api';
    
    // 构建基本URL
    let url = `${base}/cameras/${cameraId}/stream`;
    
    // 如果提供了操作选项，添加对应的查询参数
    if (options?.operation_id) {
      // 确保operation_id是有效的数字
      const opId = typeof options.operation_id === 'string' 
        ? parseInt(options.operation_id) 
        : options.operation_id;
        
      if (!isNaN(opId) && opId > 0) {
        url += `?operation_id=${opId}`;
        
        // 添加操作类型（如果指定）
        if (options.operation_type) {
          url += `&operation_type=${options.operation_type}`;
        }
      }
    }
    
    console.log('获取摄像头流URL:', url);
    return url;
  }

  /**
   * 从设备配置中获取摄像头ID
   * @param device 设备对象
   * @returns 摄像头ID或null
   */
  getCameraIdFromDevice(device: Device): string | null {
    if (device.type !== 'camera' || !device.config) {
      return null;
    }
    
    const source = device.config.source;
    if (!source) {
      return null;
    }
    
    if (source.startsWith('device:')) {
      const deviceId = source.split(':')[1];
      return `camera_${deviceId}`;
    } else if (source.startsWith('rtsp:')) {
      return `camera_${device.id}`;
    }
    
    return null;
  }
}

export const cameraService = new CameraServiceImpl();