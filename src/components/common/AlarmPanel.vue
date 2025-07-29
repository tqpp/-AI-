<template>
  <div class="alarm-panel" :class="panelClass">
    <div class="alarm-panel__header">
      <q-icon name="warning" size="24px" />
      <span class="alarm-panel__title">{{ alarmTitle }}</span>
      <q-space />
      <q-btn
        flat
        round
        dense
        icon="close"
        @click="closePanel"
      />
    </div>
    <div class="alarm-panel__content">
      <div v-for="(alarm, index) in activeAlarms" :key="index" class="alarm-item">
        <div class="alarm-item__icon">
          <q-icon :name="getAlarmIcon(alarm.level)" size="20px" />
        </div>
        <div class="alarm-item__content">
          <div class="alarm-item__title">{{ alarm.title }}</div>
          <div class="alarm-item__message">{{ alarm.message }}</div>
          <div class="alarm-item__time">{{ formatTime(alarm.timestamp) }}</div>
        </div>
        <div class="alarm-item__actions">
          <q-btn
            flat
            round
            dense
            icon="check_circle"
            @click="acknowledgeAlarm(alarm.id)"
            :disable="alarm.acknowledged"
            :color="alarm.acknowledged ? 'positive' : 'white'"
          />
        </div>
      </div>
    </div>
    <div class="alarm-panel__footer">
      <q-btn
        flat
        :label="t('alarmPanel.actions.acknowledgeAll')"
        icon="done_all"
        @click="acknowledgeAllAlarms"
        :disable="allAcknowledged"
      />
      <q-btn
        flat
        :icon="alarmStore.isSoundEnabled ? 'volume_up' : 'volume_off'"
        @click="alarmStore.toggleSound"
      />
      <q-space />
      <span class="alarm-count">{{ t('alarmPanel.status.alarmCount', { count: activeAlarms.length }) }}</span>
      <q-chip
        v-if="alarmStore.isEmergencyStop"
        color="negative"
        text-color="white"
        icon="warning"
        :label="t('alarmPanel.status.emergencyStop')"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useAlarmStore } from '../../stores/alarm'
import { date, useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const $q = useQuasar()
let alarmSound

onMounted(() => {
  alarmSound = new Audio('/sounds/alarm.mp3')
})

onUnmounted(() => {
  if (alarmSound) {
    alarmSound.pause()
    alarmSound = null
  }
})

// 定义组件属性
const props = defineProps({
  level: {
    type: String,
    default: 'warning',
    validator: (val) => ['info', 'warning', 'error', 'critical'].includes(val)
  }
})

const alarmStore = useAlarmStore()

// 计算属性：活跃告警列表
const activeAlarms = computed(() => {
  const alarms = alarmStore.activeAlarms
  if (alarms.some(alarm => alarm.level === 'critical' && !alarm.acknowledged)) {
    if (alarmSound && alarmSound.paused) {
      alarmSound.play()
    }
    navigator.vibrate && navigator.vibrate([200, 100, 200])
  }
  return alarms
})

// 计算属性：是否所有告警都已确认
const allAcknowledged = computed(() => {
  return activeAlarms.value.every(alarm => alarm.acknowledged)
})

// 计算属性：面板样式类
const panelClass = computed(() => {
  return `alarm-panel--${props.level}`
})

// 计算属性：告警标题
const alarmTitle = computed(() => {
  switch (props.level) {
    case 'info':
      return t('alarmPanel.title.info')
    case 'warning':
      return t('alarmPanel.title.warning')
    case 'error':
      return t('alarmPanel.title.error')
    case 'critical':
      return t('alarmPanel.title.critical')
    default:
      return t('alarmPanel.title.default')
  }
})

// 获取告警图标
function getAlarmIcon(level) {
  switch (level) {
    case 'info':
      return 'info'
    case 'warning':
      return 'warning'
    case 'error':
      return 'error'
    case 'critical':
      return 'dangerous'
    default:
      return 'notification_important'
  }
}

// 格式化时间
function formatTime(timestamp) {
  return date.formatDate(timestamp, 'YYYY-MM-DD HH:mm:ss')
}

// 确认单个告警
function acknowledgeAlarm(id) {
  alarmStore.acknowledgeAlarm(id)
  if (alarmSound) {
    alarmSound.pause()
    alarmSound.currentTime = 0
  }
  $q.notify({
    message: t('alarmPanel.notifications.alarmAcknowledged'),
    color: 'positive',
    position: 'bottom-right',
    timeout: 2000
  })
}

// 确认所有告警
function acknowledgeAllAlarms() {
  alarmStore.acknowledgeAllAlarms()
  if (alarmSound) {
    alarmSound.pause()
    alarmSound.currentTime = 0
  }
  $q.notify({
    message: t('alarmPanel.notifications.allAlarmsAcknowledged'),
    color: 'positive',
    position: 'bottom-right',
    timeout: 2000
  })
}

// 关闭告警面板
function closePanel() {
  alarmStore.hideAlarmPanel()
}
</script>

<style lang="scss" scoped>
.alarm-panel {
  position: fixed;
  bottom: 20px;
  left: 20px;
  width: 400px;
  max-height: 500px;
  background-color: var(--dark-surface);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  z-index: 9000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-left: 4px solid;
  animation: slide-in 0.3s ease-out;
  
  &--info {
    border-left-color: var(--status-blue);
  }
  
  &--warning {
    border-left-color: var(--status-yellow);
  }
  
  &--error {
    border-left-color: var(--status-red);
  }
  
  &--critical {
    border-left-color: var(--status-red);
    animation: pulse-border 2s infinite;
  }
  
  &__header {
    display: flex;
    align-items: center;
    padding: 16px;
    background-color: rgba(0, 0, 0, 0.2);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    .q-icon {
      margin-right: 8px;
    }
  }
  
  &__title {
    font-size: 18px;
    font-weight: 500;
  }
  
  &__content {
    flex: 1;
    overflow-y: auto;
    max-height: 350px;
    padding: 8px 0;
  }
  
  &__footer {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    background-color: rgba(0, 0, 0, 0.2);
    
    .alarm-count {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.7);
    }
  }
}

.alarm-item {
  display: flex;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  
  &:last-child {
    border-bottom: none;
  }
  
  &__icon {
    margin-right: 12px;
    display: flex;
    align-items: flex-start;
    padding-top: 2px;
  }
  
  &__content {
    flex: 1;
  }
  
  &__title {
    font-weight: 500;
    margin-bottom: 4px;
  }
  
  &__message {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 4px;
  }
  
  &__time {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
  }
  
  &__actions {
    display: flex;
    align-items: center;
  }
}

@keyframes slide-in {
  from { transform: translateX(-100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes pulse-border {
  0% { border-left-color: var(--status-red); box-shadow: 0 0 10px rgba(255, 0, 0, 0.5); }
  50% { border-left-color: var(--status-red); box-shadow: 0 0 20px rgba(255, 0, 0, 0.8); }
  100% { border-left-color: var(--status-red); box-shadow: 0 0 10px rgba(255, 0, 0, 0.5); }
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

@keyframes vibrate {
  0% { transform: translate(0); }
  25% { transform: translate(-2px, 2px); }
  50% { transform: translate(2px, -2px); }
  75% { transform: translate(-2px, -2px); }
  100% { transform: translate(0); }
}

.alarm-panel {
  background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  
  &--critical {
    animation: 
      pulse-border 2s infinite,
      vibrate 0.3s infinite,
      blink 1s infinite;
  }
  
  &--error {
    animation: pulse-border 2s infinite;
  }
  
  &__header {
    background: linear-gradient(180deg, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.2));
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
  
  &__content {
    &::-webkit-scrollbar {
      width: 8px;
    }
    
    &::-webkit-scrollbar-track {
      background: rgba(0, 0, 0, 0.2);
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 4px;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }
  }
  
  .alarm-item {
    transition: background-color 0.3s;
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.05);
    }
  }
}
</style>