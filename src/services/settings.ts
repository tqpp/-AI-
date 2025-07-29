import { apiService } from './api';

// Interface for System Settings
export interface SystemSettings {
  auto_save_interval: number;
  data_retention: string;
  alarm_threshold: number;
  language: string;
}

// Interface for MES Settings
export interface MesSettings {
  server_url: string;
  api_key: string;
}

// Interface for Device
export interface Device {
  id: number;
  name: string;
  type: string;
  model?: string;
  status: 'online' | 'offline' | 'error';
  config: any;
}

// Service class
export class SettingsService {
  /**
   * 获取系统设置
   */
  async getSystemSettings(): Promise<SystemSettings> {
    return apiService.get<SystemSettings>('/settings/system');
  }

  /**
   * 更新系统设置
   */
  async updateSystemSettings(settings: Partial<SystemSettings>): Promise<SystemSettings> {
    return apiService.put<SystemSettings>('/settings/system', settings);
  }

  /**
   * 获取MES设置
   */
  async getMesSettings(): Promise<MesSettings> {
    return apiService.get<MesSettings>('/settings/mes');
  }

  /**
   * 更新MES设置
   */
  async updateMesSettings(settings: Partial<MesSettings>): Promise<MesSettings> {
    return apiService.put<MesSettings>('/settings/mes', settings);
  }

  /**
   * 获取所有设备
   */
  async getDevices(type?: string): Promise<Device[]> {
    const params = type ? { type } : undefined;
    return apiService.get<Device[]>('/settings/devices', { params } as any);
  }

  /**
   * 获取单个设备
   */
  async getDevice(id: number): Promise<Device> {
    return apiService.get<Device>(`/settings/devices/${id}`);
  }

  /**
   * 创建设备
   */
  async createDevice(device: Omit<Device, 'id' | 'status'>): Promise<Device> {
    return apiService.post<Device>('/settings/devices', device);
  }

  /**
   * 更新设备
   */
  async updateDevice(id: number, device: Partial<Omit<Device, 'id'>>): Promise<Device> {
    return apiService.put<Device>(`/settings/devices/${id}`, device);
  }

  /**
   * 删除设备
   */
  async deleteDevice(id: number): Promise<void> {
    await apiService.delete(`/settings/devices/${id}`);
  }

  /**
   * 更新设备状态
   */
  async updateDeviceStatus(id: number, status: 'online' | 'offline' | 'error'): Promise<Device> {
    return apiService.put<Device>(`/settings/devices/${id}/status?status=${status}`);
  }
}

export const settingsService = new SettingsService(); 