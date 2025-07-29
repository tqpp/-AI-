<template>
  <q-page class="dashboard-page q-pa-sm">
    <div class="row q-col-gutter-sm">
      <!-- 系统状态卡片 -->
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="dashboard-card">
          <q-card-section class="q-pa-sm">
            <div class="text-subtitle1 q-mb-xs">{{ t('dashboard.systemStatus.title') }}</div>
            <div class="row items-center">
              <q-icon
                :name="getStatusIcon(systemStatus.status)"
                :color="getStatusColor(systemStatus.status)"
                size="32px"
                class="q-mr-sm"
              />
              <div>
                <div class="text-h6">{{ systemStatus.message && t(systemStatus.message) }}</div>
                <div class="text-caption">{{ t('dashboard.systemStatus.uptime') }}: {{ formatUptime(systemStatus.uptime) }}</div>
              </div>
            </div>
            <q-linear-progress
              :value="systemStatus.resources?.cpu ? systemStatus.resources.cpu / 100 : 0"
              :color="getResourceColor(systemStatus.resources?.cpu)"
              class="q-mt-xs"
              size="xs"
            />
            <div class="text-caption q-mt-xs">CPU: {{ systemStatus.resources?.cpu || 0 }}%</div>
            
            <q-linear-progress
              :value="systemStatus.resources?.memory ? systemStatus.resources.memory / 100 : 0"
              :color="getResourceColor(systemStatus.resources?.memory)"
              class="q-mt-xs"
              size="xs"
            />
            <div class="text-caption q-mt-xs">{{ t('dashboard.systemStatus.memory') }}: {{ systemStatus.resources?.memory || 0 }}%</div>
            
            <q-linear-progress
              :value="systemStatus.resources?.disk ? systemStatus.resources.disk / 100 : 0"
              :color="getResourceColor(systemStatus.resources?.disk)"
              class="q-mt-xs"
              size="xs"
            />
            <div class="text-caption q-mt-xs">{{ t('dashboard.systemStatus.disk') }}: {{ systemStatus.resources?.disk || 0 }}%</div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 设备状态卡片 -->
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="dashboard-card">
          <q-card-section class="q-pa-sm">
            <div class="text-subtitle1 q-mb-xs">{{ t('dashboard.deviceStatus.title') }}</div>
            <div class="row items-center">
              <div class="text-h6">{{ deviceStatusSummary.online_rate }}%</div>
              <div class="q-ml-sm text-caption">{{ t('dashboard.deviceStatus.onlineRate') }}</div>
            </div>
            
            <div class="row q-mt-xs">
              <div class="col-3">
                <div class="text-body1">{{ deviceStatusSummary.total }}</div>
                <div class="text-caption">{{ t('dashboard.deviceStatus.total') }}</div>
              </div>
              <div class="col-3">
                <div class="text-body1 text-positive">{{ deviceStatusSummary.online }}</div>
                <div class="text-caption">{{ t('dashboard.deviceStatus.online') }}</div>
              </div>
              <div class="col-3">
                <div class="text-body1 text-negative">{{ deviceStatusSummary.offline }}</div>
                <div class="text-caption">{{ t('dashboard.deviceStatus.offline') }}</div>
              </div>
              <div class="col-3">
                <div class="text-body1 text-warning">{{ deviceStatusSummary.error }}</div>
                <div class="text-caption">{{ t('dashboard.deviceStatus.error') }}</div>
              </div>
            </div>
            
            <div class="row q-mt-sm">
              <div class="col-3">
                <div class="text-body1">{{ deviceStatusSummary.cameras }}</div>
                <div class="text-caption">{{ t('dashboard.deviceStatus.cameras') }}</div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 今日检测统计卡片 -->
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="dashboard-card">
          <q-card-section class="q-pa-sm">
            <div class="text-subtitle1 q-mb-xs">{{ t('dashboard.detectionStats.title') }}</div>
            <div class="row items-center">
                <div class="text-h5">{{ detectionStats.total }}</div>
              <q-chip
                :color="detectionStats.change >= 0 ? 'positive' : 'negative'"
                text-color="white"
                class="q-ml-sm"
                dense
              >
                {{ detectionStats.change >= 0 ? '+' : '' }}{{ detectionStats.change }}%
              </q-chip>
              </div>
            <div class="text-caption">
              {{ t('dashboard.detectionStats.comparedToYesterday', { 
                count: detectionStats.yesterday_total || 0,
                change: detectionStats.change >= 0 ? t('dashboard.detectionStats.increase') : t('dashboard.detectionStats.decrease')
              }) }}
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 缺陷统计卡片 -->
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="dashboard-card">
          <q-card-section class="q-pa-sm">
            <div class="text-subtitle1 q-mb-xs">{{ t('dashboard.defectStats.title') }}</div>
            <div class="row items-center">
                <div class="text-h5">{{ defectStats.total }}</div>
              <q-chip
                :color="defectStats.change <= 0 ? 'positive' : 'negative'"
                text-color="white"
                class="q-ml-sm"
                dense
              >
                {{ defectStats.change >= 0 ? '+' : '' }}{{ defectStats.change }}%
              </q-chip>
              </div>
            <div class="text-caption">
              {{ t('dashboard.defectStats.comparedToYesterday', { 
                count: defectStats.yesterday_total || 0,
                change: defectStats.change >= 0 ? t('dashboard.defectStats.increase') : t('dashboard.defectStats.decrease')
              }) }}
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 检测准确率卡片 -->
      <div class="col-12 col-sm-12 col-md-6">
        <q-card class="dashboard-card">
          <q-card-section class="q-pa-sm">
            <div class="text-subtitle1 q-mb-xs">{{ t('dashboard.accuracy.title') }}</div>
            <div class="row items-center justify-between">
              <div class="col-6">
                <div class="text-h5">{{ accuracy.value }}%</div>
                <q-chip
                  :color="accuracy.change >= 0 ? 'positive' : 'negative'"
                  text-color="white"
                  class="q-mt-xs"
                  dense
                >
                  {{ accuracy.change >= 0 ? '+' : '' }}{{ accuracy.change }}%
                </q-chip>
                <div class="text-caption q-mt-xs">
                  {{ t('dashboard.accuracy.comparedToYesterday', { 
                    value: accuracy.yesterday_accuracy || 0,
                    change: accuracy.change >= 0 ? t('dashboard.accuracy.improve') : t('dashboard.accuracy.decrease')
                  }) }}
                </div>
              </div>
              <div class="col-6 text-center">
                <q-circular-progress
                  :value="accuracy.value"
                  size="100px"
                  :thickness="0.2"
                  color="primary"
                  track-color="grey-3"
                  class="q-mb-xs"
                >
                  <div class="text-subtitle1">{{ accuracy.value }}%</div>
                  <div class="text-caption">{{ t('dashboard.accuracy.rate') }}</div>
                </q-circular-progress>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 最近告警卡片 -->
      <div class="col-12 col-sm-12 col-md-6">
        <q-card class="dashboard-card">
          <q-card-section class="q-pa-sm row items-center justify-between">
            <div class="text-subtitle1">{{ t('dashboard.alerts.title') }}</div>
            <q-btn flat round icon="refresh" size="sm" dense @click="getRecentAlerts" />
          </q-card-section>
          <q-separator />
          <q-card-section class="q-pa-sm alert-list">
            <q-list dense>
              <q-item v-for="alert in alerts" :key="alert.id" class="q-py-xs" :clickable="!alert.is_read" @click="markAlertRead(alert.id)">
                <q-item-section avatar>
                  <q-icon :name="getAlertIcon(alert.type)" :color="getAlertColor(alert.type)" size="xs" />
                </q-item-section>
                <q-item-section>
                  <q-item-label lines="1">{{ alert.message }}</q-item-label>
                  <q-item-label caption>
                    {{ formatDate(alert.timestamp) }}
                    <span v-if="alert.device_name"> | {{ alert.device_name }}</span>
                  </q-item-label>
                </q-item-section>
                <q-item-section side v-if="!alert.is_read">
                  <q-badge color="red" :label="t('dashboard.alerts.new')" />
                </q-item-section>
              </q-item>
              <q-item v-if="alerts.length === 0">
                <q-item-section>
                  <q-item-label>{{ t('dashboard.alerts.noAlerts') }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <!-- 检测趋势图表 -->
      <div class="col-12">
        <q-card class="dashboard-card">
          <q-card-section class="q-pa-sm">
            <div class="text-subtitle1 q-mb-xs">{{ t('dashboard.trend.title') }}</div>
          </q-card-section>
          <q-separator />
          <q-card-section class="chart-container">
            <canvas ref="trendChart"></canvas>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useDashboard } from '../services/dashboard';
import { format, fromUnixTime } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import Chart from 'chart.js/auto';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// 获取仪表板服务
const { 
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
  markAlertAsRead,
  getDeviceStatusSummary,
  getDetectionTrends,
  refreshAllData
} = useDashboard();

const trendChart = ref(null);
let chart = null;
let refreshInterval = null;

// 格式化日期
const formatDate = (timestamp) => {
  try {
    const date = fromUnixTime(timestamp / 1000);
    return format(date, 'yyyy-MM-dd HH:mm', { locale: zhCN });
  } catch (e) {
    return '无效日期';
  }
};

// 格式化运行时间
const formatUptime = (hours) => {
  if (!hours) return t('dashboard.systemStatus.unknown');
  
  const days = Math.floor(hours / 24);
  const remainingHours = Math.floor(hours % 24);
  
  if (days > 0) {
    return `${days}${t('dashboard.systemStatus.days')}${remainingHours}${t('dashboard.systemStatus.hours')}`;
  } else {
    return `${remainingHours}${t('dashboard.systemStatus.hours')}`;
  }
};

// 获取状态图标
const getStatusIcon = (status) => {
  switch (status) {
    case 'normal':
      return 'check_circle';
    case 'warning':
      return 'warning';
    case 'error':
      return 'error';
    default:
      return 'help';
  }
};

// 获取状态颜色
const getStatusColor = (status) => {
  switch (status) {
    case 'normal':
      return 'positive';
    case 'warning':
      return 'warning';
    case 'error':
      return 'negative';
    default:
      return 'grey';
  }
};

// 获取资源使用率颜色
const getResourceColor = (value) => {
  if (!value) return 'grey';
  if (value > 90) return 'negative';
  if (value > 70) return 'warning';
  return 'positive';
};

// 获取告警图标
const getAlertIcon = (type) => {
  switch (type) {
    case 'ERROR':
      return 'error';
    case 'WARNING':
      return 'warning';
    case 'INFO':
      return 'info';
    default:
      return 'help';
  }
};

// 获取告警颜色
const getAlertColor = (type) => {
  switch (type) {
    case 'ERROR':
      return 'negative';
    case 'WARNING':
      return 'warning';
    case 'INFO':
      return 'info';
    default:
      return 'grey';
  }
};

// 标记告警为已读
const markAlertRead = async (alertId) => {
  try {
    await markAlertAsRead(alertId);
    // 刷新告警列表
    await getRecentAlerts();
  } catch (error) {
    console.error('标记告警为已读失败', error);
  }
};

// 初始化趋势图表
const initTrendChart = () => {
  if (!trendChart.value) return;
  
  const ctx = trendChart.value.getContext('2d');
  
  if (chart) {
    chart.destroy();
  }
  
  const dates = detectionTrends.value.map(item => item.date);
  const totals = detectionTrends.value.map(item => item.total);
  const passes = detectionTrends.value.map(item => item.pass);
  const fails = detectionTrends.value.map(item => item.fail);
  
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [
        {
          label: t('dashboard.trend.total'),
          data: totals,
          borderColor: '#1976D2',
          backgroundColor: 'rgba(25, 118, 210, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: t('dashboard.trend.pass'),
          data: passes,
          borderColor: '#21BA45',
          backgroundColor: 'rgba(33, 186, 69, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: t('dashboard.trend.fail'),
          data: fails,
          borderColor: '#C10015',
          backgroundColor: 'rgba(193, 0, 21, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            boxWidth: 12,
            font: {
              size: 11
            }
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            font: {
              size: 10
            }
          }
        },
        x: {
          ticks: {
            font: {
              size: 10
            }
          }
        }
      }
    }
  });
};

// 加载所有数据
const loadAllData = async () => {
  try {
    await refreshAllData();
    // 更新趋势图表
    initTrendChart();
  } catch (error) {
    console.error('加载仪表板数据失败', error);
  }
};

// 组件挂载
onMounted(async () => {
  await loadAllData();
  
  // 设置定时刷新 (每30秒)
  refreshInterval = setInterval(loadAllData, 30000);
});

// 组件卸载
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
  
  if (chart) {
    chart.destroy();
  }
});
</script>

<style lang="scss" scoped>
.dashboard-page {
  max-width: 100%;
  overflow-x: hidden;
  background: var(--dark-page);
}

.dashboard-card {
  height: 100%;
  background: var(--dark-card);
  transition: all 0.2s ease;
  overflow: hidden;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  }
}

.chart-container {
  height: 250px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.02);
  padding: 8px;
}

.alert-list {
  max-height: 200px;
  overflow-y: auto;
}

// 修复滚动条样式问题
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
</style>