/**
 * 告警数据持久化存储工具
 */

// 本地存储键名
const STORAGE_KEY = 'industrial-ocr-alarms'
const SOUND_SETTINGS_KEY = 'alarm-sound-settings'

// 保存告警数据到本地存储
export function saveAlarms(alarms) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(alarms))
    return true
  } catch (error) {
    console.error('保存告警数据失败:', error)
    return false
  }
}

// 从本地存储加载告警数据
export function loadAlarms() {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    return data ? JSON.parse(data) : []
  } catch (error) {
    console.error('加载告警数据失败:', error)
    return []
  }
}

// 保存声音设置
export function saveSoundSettings(enabled) {
  try {
    localStorage.setItem(SOUND_SETTINGS_KEY, JSON.stringify({ enabled }))
    return true
  } catch (error) {
    console.error('保存声音设置失败:', error)
    return false
  }
}

// 加载声音设置
export function loadSoundSettings() {
  try {
    const data = localStorage.getItem(SOUND_SETTINGS_KEY)
    return data ? JSON.parse(data).enabled : true
  } catch (error) {
    console.error('加载声音设置失败:', error)
    return true
  }
}