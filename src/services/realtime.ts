import { ref } from 'vue';
import { apiService } from './api';

// 检测结果类型
export interface DetectionResult {
  status: 'pass' | 'fail';
  timestamp: number;
  text: string;
  confidence: number;
}

// WebSocket连接URL
const WS_URL = 'ws://localhost:3000/ws/detection';

// 实时检测服务
export const useRealtime = () => {
  const detectionResult = ref<DetectionResult>({
    status: 'pass',
    timestamp: Date.now(),
    text: '',
    confidence: 0
  });
  
  let ws: WebSocket | null = null;

  // 初始化WebSocket连接
  const initWebSocket = () => {
    ws = new WebSocket(WS_URL);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data) as DetectionResult;
      detectionResult.value = data;
    };

    ws.onclose = () => {
      console.log('WebSocket连接已关闭');
      ws = null;
      // 尝试重新连接
      setTimeout(initWebSocket, 5000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
      ws?.close();
    };
  };

  // 获取最新检测结果
  const getLatestResult = async () => {
    const data = await apiService.get<DetectionResult>('/detection/latest');
    detectionResult.value = data;
    return detectionResult.value;
  };

  // 启动实时检测
  const startRealtime = () => {
    if (!ws) {
      initWebSocket();
    }
  };

  // 停止实时检测
  const stopRealtime = () => {
    if (ws) {
      ws.close();
      ws = null;
    }
  };

  return {
    detectionResult,
    getLatestResult,
    startRealtime,
    stopRealtime
  };
};