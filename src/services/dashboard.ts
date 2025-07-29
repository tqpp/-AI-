import { ref } from 'vue';
import { apiService } from './api';

// 系统状态类型
export interface SystemStatus {
  status: 'normal' | 'warning' | 'error';
  uptime: number;
  message?: string;
  resources?: {
    cpu: number;
    memory: number;
    disk: number;
  };
}

// 统计数据类型
export interface Statistics {
  total: number;
  change: number;
  today?: string;
  yesterday_total?: number;
}

// 准确率数据类型
export interface Accuracy {
  value: number;
  change: number;
  today_total?: number;
  today_pass?: number;
  yesterday_accuracy?: number;
}

// 告警信息类型
export interface Alert {
  id: string;
  type: string;
  message: string;
  timestamp: number;
  device_name?: string;
  is_read?: boolean;
}

// 设备状态摘要
export interface DeviceStatusSummary {
  total: number;
  online: number;
  offline: number;
  error: number;
  cameras: number;
  online_rate: number;
}

// 检测趋势数据
export interface DetectionTrendItem {
  date: string;
  total: number;
  pass: number;
  fail: number;
}

// Dashboard服务
export const useDashboard = () => {
  const systemStatus = ref<SystemStatus>({ status: 'normal', uptime: 0 });
  const detectionStats = ref<Statistics>({ total: 0, change: 0 });
  const defectStats = ref<Statistics>({ total: 0, change: 0 });
  const accuracy = ref<Accuracy>({ value: 0, change: 0 });
  const alerts = ref<Alert[]>([]);
  const deviceStatusSummary = ref<DeviceStatusSummary>({
    total: 0,
    online: 0,
    offline: 0,
    error: 0,
    cameras: 0,
    online_rate: 0
  });
  const detectionTrends = ref<DetectionTrendItem[]>([]);

  // 获取系统状态
  const getSystemStatus = async () => {
    const data = await apiService.get<SystemStatus>('/dashboard/system-status');
    systemStatus.value = data;
    return systemStatus.value;
  };

  // 获取今日检测统计
  const getDetectionStats = async () => {
    const data = await apiService.get<Statistics>('/dashboard/detection-stats');
    detectionStats.value = data;
    return detectionStats.value;
  };

  // 获取缺陷统计
  const getDefectStats = async () => {
    const data = await apiService.get<Statistics>('/dashboard/defect-stats');
    defectStats.value = data;
    return defectStats.value;
  };

  // 获取准确率
  const getAccuracy = async () => {
    const data = await apiService.get<Accuracy>('/dashboard/accuracy');
    accuracy.value = data;
    return accuracy.value;
  };

  // 获取最近告警
  const getRecentAlerts = async () => {
    const data = await apiService.get<Alert[]>('/dashboard/alerts');
    alerts.value = data;
    return alerts.value;
  };

  // 创建新告警
  const createAlert = async (message: string, alertType: string = 'INFO', deviceId?: number) => {
    const params = new URLSearchParams();
    params.append('message', message);
    params.append('alert_type', alertType);
    if (deviceId) {
      params.append('device_id', deviceId.toString());
    }
    
    return await apiService.post('/dashboard/alerts', params);
  };

  // 标记告警为已读
  const markAlertAsRead = async (alertId: string) => {
    return await apiService.put(`/dashboard/alerts/${alertId}/read`);
  };
  
  // 获取设备状态摘要
  const getDeviceStatusSummary = async () => {
    const data = await apiService.get<DeviceStatusSummary>('/dashboard/device-status');
    deviceStatusSummary.value = data;
    return deviceStatusSummary.value;
  };
  
  // 获取检测趋势
  const getDetectionTrends = async (days: number = 7) => {
    const data = await apiService.get<DetectionTrendItem[]>(`/dashboard/detection-trends?days=${days}`);
    detectionTrends.value = data;
    return detectionTrends.value;
  };

  // 刷新所有仪表盘数据
  const refreshAllData = async () => {
    try {
      await Promise.all([
        getSystemStatus(),
        getDetectionStats(),
        getDefectStats(),
        getAccuracy(),
        getRecentAlerts(),
        getDeviceStatusSummary(),
        getDetectionTrends()
      ]);
      return true;
    } catch (error) {
      console.error('刷新仪表盘数据失败', error);
      return false;
    }
  };

  return {
    systemStatus,
    detectionStats,
    defectStats,
    accuracy,
    alerts,
    deviceStatusSummary,
    detectionTrends,
    getSystemStatus,
    getDetectionStats,
    getDefectStats,
    getAccuracy,
    getRecentAlerts,
    createAlert,
    markAlertAsRead,
    getDeviceStatusSummary,
    getDetectionTrends,
    refreshAllData
  };
};