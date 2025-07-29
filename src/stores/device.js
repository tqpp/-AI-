import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 设备状态管理Store
 * 管理相机、模型和设备连接状态
 */
export const useDeviceStore = defineStore('device', () => {
  // 相机状态 (connected, disconnected, initializing)
  const cameraStatus = ref('disconnected')
  
  // 模型状态 (loaded, unloaded, loading)
  const modelStatus = ref('unloaded')
  
  // 设备连接状态 (connected, disconnected, connecting)
  const connectionStatus = ref('disconnected')
  
  // 相机配置
  const cameraConfig = ref({
    resolution: '1920x1080',
    fps: 30,
    exposure: 100,
    gain: 1.0,
    autoFocus: false
  })
  
  // 模型配置
  const modelConfig = ref({
    name: 'industrial-ocr-v1',
    version: '1.0.0',
    threshold: 0.85,
    maxDetections: 10,
    processingTime: 0
  })
  
  // 设备信息
  const deviceInfo = ref({
    id: '',
    name: '',
    type: '',
    ipAddress: '',
    lastConnected: null
  })
  
  // 连接相机
  async function connectCamera() {
    cameraStatus.value = 'initializing'
    
    try {
      // 模拟相机连接过程
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // 连接成功
      cameraStatus.value = 'connected'
      return true
    } catch (error) {
      // 连接失败
      cameraStatus.value = 'disconnected'
      return false
    }
  }
  
  // 断开相机连接
  function disconnectCamera() {
    cameraStatus.value = 'disconnected'
  }
  
  // 加载模型
  async function loadModel(modelName = 'industrial-ocr-v1') {
    modelStatus.value = 'loading'
    
    try {
      // 模拟模型加载过程
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      // 加载成功
      modelStatus.value = 'loaded'
      modelConfig.value.name = modelName
      return true
    } catch (error) {
      // 加载失败
      modelStatus.value = 'unloaded'
      return false
    }
  }
  
  // 卸载模型
  function unloadModel() {
    modelStatus.value = 'unloaded'
  }
  
  // 连接设备
  async function connectDevice(deviceId, deviceType) {
    connectionStatus.value = 'connecting'
    
    try {
      // 模拟设备连接过程
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // 连接成功
      connectionStatus.value = 'connected'
      deviceInfo.value = {
        id: deviceId,
        type: deviceType,
        name: `${deviceType}-${deviceId}`,
        ipAddress: '192.168.1.100', // 模拟IP地址
        lastConnected: new Date()
      }
      return true
    } catch (error) {
      // 连接失败
      connectionStatus.value = 'disconnected'
      return false
    }
  }
  
  // 断开设备连接
  function disconnectDevice() {
    connectionStatus.value = 'disconnected'
  }
  
  // 更新相机配置
  function updateCameraConfig(config) {
    cameraConfig.value = {
      ...cameraConfig.value,
      ...config
    }
  }
  
  // 更新模型配置
  function updateModelConfig(config) {
    modelConfig.value = {
      ...modelConfig.value,
      ...config
    }
  }
  
  // 计算属性：系统是否就绪
  const isSystemReady = computed(() => {
    return cameraStatus.value === 'connected' && 
           modelStatus.value === 'loaded' && 
           connectionStatus.value === 'connected'
  })
  
  return {
    // 状态
    cameraStatus,
    modelStatus,
    connectionStatus,
    cameraConfig,
    modelConfig,
    deviceInfo,
    isSystemReady,
    
    // 方法
    connectCamera,
    disconnectCamera,
    loadModel,
    unloadModel,
    connectDevice,
    disconnectDevice,
    updateCameraConfig,
    updateModelConfig
  }
})