import { defineStore } from 'pinia'
import { ref, computed, onMounted, watch } from 'vue'
import { saveAlarms, loadAlarms, saveSoundSettings, loadSoundSettings } from '../utils/alarmStorage'
import { useDeviceStore } from './device'

/**
 * 告警管理Store
 * 管理系统告警、通知和紧急状态
 */
export const useAlarmStore = defineStore('alarm', () => {
  // 告警列表
  const alarms = ref([])
  
  // 告警面板是否可见
  const isPanelVisible = ref(false)
  
  // 紧急停止状态
  const isEmergencyStop = ref(false)
  
  // 告警音效是否启用
  const isSoundEnabled = ref(loadSoundSettings())

  // 设备状态监控
  const deviceStore = useDeviceStore()

  // 初始化告警数据
  onMounted(() => {
    alarms.value = loadAlarms()
  })

  // 监听设备状态变化
  watch(() => deviceStore.cameraStatus, (newStatus, oldStatus) => {
    if (newStatus === 'disconnected' && oldStatus === 'connected') {
      addAlarm({
        level: 'error',
        message: '相机连接已断开',
        source: 'camera'
      })
    }
  })

  watch(() => deviceStore.modelStatus, (newStatus, oldStatus) => {
    if (newStatus === 'unloaded' && oldStatus === 'loaded') {
      addAlarm({
        level: 'warning',
        message: '模型已卸载',
        source: 'model'
      })
    }
  })

  watch(() => deviceStore.connectionStatus, (newStatus, oldStatus) => {
    if (newStatus === 'disconnected' && oldStatus === 'connected') {
      addAlarm({
        level: 'error',
        message: '设备连接已断开',
        source: 'device'
      })
    }
  })
  
  // 添加新告警
  function addAlarm(alarm) {
    // 保存告警数据
    const result = saveAlarms(alarms.value)
    if (!result) {
      console.error('告警数据保存失败')
    }
    // 生成唯一ID
    const id = Date.now()
    
    // 添加告警到列表
    alarms.value.push({
      id,
      timestamp: Date.now(),
      acknowledged: false,
      ...alarm
    })
    
    // 显示告警面板
    isPanelVisible.value = true
  }
  
  // 确认告警
  function acknowledgeAlarm(id) {
    const alarm = alarms.value.find(a => a.id === id)
    if (alarm) {
      alarm.acknowledged = true
    }
  }
  
  // 确认所有告警
  function acknowledgeAllAlarms() {
    alarms.value.forEach(alarm => alarm.acknowledged = true)
  }
  
  // 删除告警
  function removeAlarm(id) {
    const index = alarms.value.findIndex(a => a.id === id)
    if (index !== -1) {
      alarms.value.splice(index, 1)
    }
  }
  
  // 清空所有告警
  function clearAlarms() {
    alarms.value = []
  }
  
  // 触发紧急停止
  function triggerEmergencyStop() {
    isEmergencyStop.value = true
    addAlarm({
      level: 'critical',
      message: 'System Emergency Stop',
      source: 'system'
    })
  }
  
  // 解除紧急停止
  function clearEmergencyStop() {
    isEmergencyStop.value = false
  }
  
  // 切换告警音效
  function toggleSound() {
    isSoundEnabled.value = !isSoundEnabled.value
    saveSoundSettings(isSoundEnabled.value)
  }
  
  // 显示告警面板
  function showAlarmPanel() {
    isPanelVisible.value = true
  }
  
  // 隐藏告警面板
  function hideAlarmPanel() {
    isPanelVisible.value = false
  }
  
  // 计算属性：活跃告警列表
  const activeAlarms = computed(() => {
    return alarms.value.filter(alarm => !alarm.acknowledged)
  })
  
  // 计算属性：最高告警等级
  const highestAlarmLevel = computed(() => {
    const levels = {
      critical: 4,
      error: 3,
      warning: 2,
      info: 1
    }
    
    return activeAlarms.value.reduce((highest, alarm) => {
      const currentLevel = levels[alarm.level] || 0
      return currentLevel > highest ? alarm.level : highest
    }, 'info')
  })
  
  return {
    // 状态
    alarms,
    isPanelVisible,
    isEmergencyStop,
    isSoundEnabled,
    activeAlarms,
    highestAlarmLevel,
    
    // 方法
    addAlarm,
    acknowledgeAlarm,
    acknowledgeAllAlarms,
    removeAlarm,
    clearAlarms,
    triggerEmergencyStop,
    clearEmergencyStop,
    toggleSound,
    showAlarmPanel,
    hideAlarmPanel
  }
})