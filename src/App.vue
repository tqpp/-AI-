<template>
  <q-layout view="hHh lpR fFf" class="industrial-app">
    <!-- 全局紧急停止按钮 -->
    <div class="emergency-stop-container">
      <industrial-icons type="industrial-button" size="lg" :active="false" @click="confirmEmergencyStop" class="emergency-stop-btn">
        <q-icon name="power_settings_new" color="negative" size="32px" />
      </industrial-icons>
    </div>

    <!-- 顶部状态栏 -->
    <q-header elevated class="bg-dark-page header-container">
      <metal-textures type="brushed" size="full" class="header-texture">
        <status-bar />
      </metal-textures>
    </q-header>

    <!-- 左侧导航抽屉 -->
    <q-drawer
      v-model="leftDrawerOpen"
      bordered
      :width="240"
      :breakpoint="700"
      class="industrial-drawer bg-dark"
    >
      <metal-textures type="carbon" size="full" class="drawer-texture">
        <q-scroll-area class="fit">
          <div class="drawer-header">
            <div class="system-logo">
              <svg width="40" height="40" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="120" height="120" rx="16" fill="#121212"/>
                <path d="M30 30H90V42H78V90H42V42H30V30Z" fill="#2A5CAA"/>
                <rect x="48" y="48" width="24" height="6" fill="#FF6B35"/>
                <rect x="48" y="60" width="24" height="6" fill="#FF6B35"/>
                <rect x="48" y="72" width="24" height="6" fill="#FF6B35"/>
              </svg>
            </div>
            <div class="system-title">{{ t('common.systemName') }}</div>
          </div>
          
          <navigation-menu />
        </q-scroll-area>
      </metal-textures>
    </q-drawer>

    <!-- 主内容区域 -->
    <q-page-container class="page-container">
      <metal-textures type="perforated" size="full" class="page-texture">
        <router-view />
      </metal-textures>
    </q-page-container>

    <!-- 全局告警面板 -->
    <alarm-panel v-if="hasActiveAlarms" :level="currentAlarmLevel" />
  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'
import StatusBar from './components/layout/StatusBar.vue'
import NavigationMenu from './components/layout/NavigationMenu.vue'
import AlarmPanel from './components/common/AlarmPanel.vue'
import MetalTextures from './components/common/MetalTextures.vue'
import IndustrialIcons from './components/common/IndustrialIcons.vue'
import { useAlarmStore } from './stores/alarm'

// 处理加载指示器
onMounted(() => {
  const loadingIndicator = document.getElementById('loading-indicator')
  if (loadingIndicator) {
    loadingIndicator.style.opacity = '0'
    setTimeout(() => {
      loadingIndicator.style.display = 'none'
    }, 500)
  }
})

const { t } = useI18n()
const $q = useQuasar()
const leftDrawerOpen = ref(true)
const alarmStore = useAlarmStore()

// 计算属性：是否有活跃告警
const hasActiveAlarms = computed(() => alarmStore.activeAlarms.length > 0)

// 计算属性：当前最高告警等级
const currentAlarmLevel = computed(() => alarmStore.highestAlarmLevel)

// 紧急停止确认
function confirmEmergencyStop() {
  $q.dialog({
    title: t('emergencyStop.title'),
    message: t('emergencyStop.message'),
    color: 'negative',
    icon: 'warning',
    persistent: true,
    ok: {
      label: t('emergencyStop.confirm'),
      color: 'negative',
      flat: false,
      'no-caps': true
    },
    cancel: {
      label: t('common.cancel'),
      color: 'dark',
      textColor: 'white',
      flat: true,
      'no-caps': true
    }
  }).onOk(() => {
    // 执行紧急停止逻辑
    alarmStore.triggerEmergencyStop()
    $q.notify({
      type: 'negative',
      message: t('emergencyStop.executed'),
      icon: 'warning'
    })
  })
}
</script>

<style lang="scss">
.industrial-app {
  height: 100vh;
  background-color: var(--q-dark-page);
  display: flex;
  flex-direction: column;
}

.emergency-stop-container {
  position: fixed;
  bottom: 20px;
  right: 0;
  z-index: 9999;
  transition: all 0.3s ease;
  transform: translateX(50px); /* 默认隐藏一半 */
  
  &:hover {
    transform: translateX(0); /* 鼠标悬停时完全显示 */
  }
}

.emergency-stop-btn {
  width: 80px;
  height: 80px;
  border: 4px solid #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(255, 0, 0, 0.7);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  &::before {
    content: '';
    position: absolute;
    top: -8px;
    left: -8px;
    right: -8px;
    bottom: -8px;
    border: 2px dashed #ff0000;
    border-radius: 50%;
    animation: rotate 10s linear infinite;
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.header-container {
  overflow: hidden;
}

.header-texture {
  height: 64px;
}

.drawer-texture {
  height: 100%;
}

.drawer-header {
  display: flex;
  align-items: center;
  padding: 16px;
  height: 80px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  
  .system-logo {
    margin-right: 12px;
  }
  
  .system-title {
    font-size: 18px;
    font-weight: 500;
    color: var(--safety-orange);
  }
}

.page-container {
  background-color: var(--dark-bg);
  flex-grow: 1;
  overflow-y: scroll !important;
}

.page-texture {
  height: 100%;
  overflow-y: scroll !important;
}

.industrial-drawer {
  .q-item {
    min-height: 60px;
    border-radius: 8px;
    margin: 4px 0;
    font-size: 18px;
    
    &.q-item--active {
      background: rgba(42, 92, 170, 0.3);
      border-left: 4px solid #2A5CAA;
    }
  }
}
</style>