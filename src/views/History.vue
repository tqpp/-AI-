<template>
  <q-page class="history-page q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- 搜索过滤器 -->
      <div class="col-12">
        <q-card class="filter-card">
          <q-card-section>
            <div class="row q-col-gutter-md items-center">
              <div class="col-12 col-md-3">
                <q-input
                  v-model="filters.searchText"
                  dense
                  outlined
                  :label="t('history.searchText')"
                  class="full-width"
                  @keyup.enter="searchRecords"
                />
              </div>
              <div class="col-12 col-md-3">
                <q-select
                  v-model="filters.status"
                  :options="['全部', '合格', '不合格']"
                  dense
                  outlined
                  :option-label="(val) => t(`history.status.${val === '全部' ? 'all' : (val === '合格' ? 'pass' : 'fail')}`)"
                  :label="t('history.status.title')"
                  class="full-width"
                  @update:model-value="searchRecords"
                />
              </div>
              <div class="col-12 col-md-4">
                <q-input
                  :model-value="formatDateRangeDisplay(filters.dateRange)"
                  dense
                  outlined
                  :label="t('history.dateRange')"
                  class="full-width"
                  readonly
                >
                  <template v-slot:append>
                    <q-icon name="event" class="cursor-pointer">
                      <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                        <q-date v-model="filters.dateRange" range @update:model-value="updateDateRange" />
                      </q-popup-proxy>
                    </q-icon>
                  </template>
                </q-input>
              </div>
              <div class="col-12 col-md-2">
                <div class="row q-col-gutter-sm">
                  <div class="col">
                    <q-btn color="primary" icon="search" :label="t('history.search')" class="full-width" @click="searchRecords" />
                  </div>
                  <div class="col">
                    <q-btn color="secondary" icon="download" :label="t('history.export_excel')" class="full-width" @click="exportToExcel" />
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 历史记录表格 -->
      <div class="col-12">
        <q-card class="table-card">
          <q-card-section>
            <q-table
              :rows="records"
              :columns="columns"
              row-key="id"
              :pagination="pagination"
              :loading="loading"
              @request="onRequest"
              class="history-table"
              binary-state-sort
            >
              <template v-slot:body-cell-status="props">
                <q-td :props="props">
                  <q-chip
                    :color="props.value === 'pass' ? 'positive' : (props.value === 'fail' ? 'negative' : 'grey')"
                    text-color="white"
                    dense
                  >
                    {{ statusText(props.value) }}
                  </q-chip>
                </q-td>
              </template>
              
              <template v-slot:body-cell-confidence="props">
                <q-td :props="props">
                  {{ props.value !== null ? `${props.value.toFixed(1)}%` : 'N/A' }}
                </q-td>
              </template>
              
              <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                  <q-btn flat round dense icon="visibility" color="info" @click="viewRecord(props.row)" />
                  <q-btn flat round dense icon="delete" color="negative" @click="confirmDelete(props.row)" />
                </q-td>
              </template>
              
              <template v-slot:no-data>
                <div class="full-width row flex-center q-pa-md">
                  <q-icon name="info" size="2em" color="grey-7" />
                  <span class="text-grey-7 q-ml-sm">{{ t('history.noData') }}</span>
                </div>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>
    
    <!-- 详情对话框 -->
    <q-dialog v-model="detailDialog" persistent>
      <q-card style="width: 700px; max-width: 90vw">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ t('history.detail.title') }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        
        <q-card-section v-if="selectedRecord">
          <div class="row q-col-gutter-md">
            <!-- 检测图像 -->
            <div class="col-12 col-md-6">
              <div class="text-subtitle2 q-mb-sm">{{ t('history.detail.originalImage') }}</div>
              <div class="image-container">
                <img :src="selectedRecord.imagePath" :alt="t('history.detail.originalImage')" class="detection-image" v-if="selectedRecord.imagePath" />
                <div class="no-image-placeholder">{{ t('history.detail.noImage') }}</div>
              </div>
            </div>
            
            <!-- 处理后图像 (如果有) -->
            <div class="col-12 col-md-6" v-if="selectedRecord.processedImagePath">
              <div class="text-subtitle2 q-mb-sm">{{ t('history.detail.processedImage') }}</div>
              <div class="image-container">
                <img :src="selectedRecord.processedImagePath" :alt="t('history.detail.processedImage')" class="detection-image" />
              </div>
            </div>
            
            <!-- 详细信息 -->
            <div class="col-12">
              <q-list separator>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>{{ t('history.detail.timestamp') }}</q-item-label>
                    <q-item-label>{{ formatDateTime(selectedRecord.timestamp) }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>{{ t('history.detail.status') }}</q-item-label>
                    <q-item-label>
                      <q-chip
                        :color="selectedRecord.status === 'pass' ? 'positive' : 'negative'"
                        text-color="white"
                        dense
                      >
                        {{ statusText(selectedRecord.status) }}
                      </q-chip>
                    </q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>{{ t('history.detail.text') }}</q-item-label>
                    <q-item-label>{{ selectedRecord.text || t('history.detail.noText') }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>{{ t('history.detail.confidence') }}</q-item-label>
                    <q-item-label>{{ selectedRecord.confidence ? `${selectedRecord.confidence.toFixed(1)}%` : 'N/A' }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item v-if="selectedRecord.deviceName">
                  <q-item-section>
                    <q-item-label caption>{{ t('history.detail.device') }}</q-item-label>
                    <q-item-label>{{ selectedRecord.deviceName }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat :label="t('common.cancel')" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
    
    <!-- 删除确认对话框 -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="warning" color="negative" text-color="white" />
          <span class="q-ml-sm">{{ t('history.delete.confirm') }}</span>
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat :label="t('common.cancel')" color="primary" v-close-popup />
          <q-btn flat :label="t('common.delete')" color="negative" @click="deleteRecord" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { detectionService, Detection } from '@/services/detection'
import { formatDate } from '@/utils/date'
import * as XLSX from 'xlsx'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const $q = useQuasar()

// 状态
const loading = ref(false)
const records = ref<Detection[]>([])
const total = ref(0)
const detailDialog = ref(false)
const deleteDialog = ref(false)
const selectedRecord = ref<Detection | null>(null)
const recordToDelete = ref<Detection | null>(null)

// 日期范围接口定义
interface DateRange {
  from: string;
  to: string;
}

// 表格配置
const columns = [
  { 
    name: 'timestamp', 
    align: 'left' as const, 
    label: t('history.columns.timestamp'), 
    field: 'timestamp', 
    format: formatDateTime 
  },
  { name: 'text', align: 'left' as const, label: t('history.columns.text'), field: 'text' },
  { name: 'confidence', align: 'center' as const, label: t('history.columns.confidence'), field: 'confidence' },
  { name: 'status', align: 'center' as const, label: t('history.columns.status'), field: 'status' },
  { name: 'deviceName', align: 'left' as const, label: t('history.columns.device'), field: 'deviceName' },
  { name: 'actions', align: 'center' as const, label: t('history.columns.actions'), field: 'actions' }
]

// 分页配置
const pagination = reactive({
  page: 1,
  rowsPerPage: 10,
  sortBy: 'timestamp',
  descending: true
})

// 监听分页变化
watch(() => pagination.page, (newPage) => {
  loadRecords()
})

// 过滤器
const filters = reactive({
  searchText: '',
  status: '全部',
  dateRange: { from: getTodayMinus(30), to: formatDate(new Date()) } as any,
  dateFrom: '',
  dateTo: ''
})

// 辅助函数
function getTodayMinus(days: number): string {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return formatDate(date)
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function statusText(status: string): string {
  switch (status) {
    case 'pass': return t('history.status.pass')
    case 'fail': return t('history.status.fail')
    case 'unknown': return t('history.status.unknown')
    default: return status
  }
}

// 加载数据
async function loadRecords() {
  loading.value = true
  
  try {
    const response = await detectionService.getDetections({
      page: pagination.page,
      perPage: pagination.rowsPerPage,
      searchText: filters.searchText || undefined,
      status: filters.status !== '全部' ? filters.status : undefined,
      dateFrom: filters.dateFrom || undefined,
      dateTo: filters.dateTo || undefined
    })
    
    records.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('加载历史记录失败:', error)
    $q.notify({
      type: 'negative',
      message: '加载历史记录失败',
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}

// 分页请求处理
function onRequest(props: any) {
  const { page, rowsPerPage } = props.pagination
  pagination.page = page
  pagination.rowsPerPage = rowsPerPage
  loadRecords()
}

// 搜索记录
function searchRecords() {
  pagination.page = 1 // 重置到第一页
  loadRecords()
}

// 更新日期范围
function updateDateRange() {
  if (filters.dateRange.from && filters.dateRange.to) {
    // 确保日期格式正确 - Quasar的q-date返回的格式是YYYY/MM/DD，需要转换为YYYY-MM-DD
    filters.dateFrom = filters.dateRange.from.replace(/\//g, '-');
    filters.dateTo = filters.dateRange.to.replace(/\//g, '-');
    console.log('日期范围:', filters.dateFrom, '至', filters.dateTo);
    searchRecords();
  }
}

// 查看记录详情
function viewRecord(record: Detection) {
  selectedRecord.value = record
  detailDialog.value = true
}

// 确认删除
function confirmDelete(record: Detection) {
  recordToDelete.value = record
  deleteDialog.value = true
}

// 删除记录
async function deleteRecord() {
  if (!recordToDelete.value) return
  
  try {
    await detectionService.deleteDetection(recordToDelete.value.id)
    
    $q.notify({
      type: 'positive',
      message: '记录已删除',
      position: 'top'
    })
    
    // 重新加载数据
    loadRecords()
  } catch (error) {
    console.error('删除记录失败:', error)
    $q.notify({
      type: 'negative',
      message: '删除记录失败',
      position: 'top'
    })
  }
}

// 组件挂载时加载数据
onMounted(() => {
  // 设置初始日期范围
  filters.dateFrom = filters.dateRange.from.replace(/\//g, '-');
  filters.dateTo = filters.dateRange.to.replace(/\//g, '-');
  
  // 加载记录
  loadRecords()
})

// 格式化日期范围字符串显示
function formatDateRangeDisplay(dateRange: any): string {
  if (!dateRange || !dateRange.from || !dateRange.to) {
    return '';
  }
  
  // 统一替换日期分隔符为横线
  const from = dateRange.from.replace(/\//g, '-');
  const to = dateRange.to.replace(/\//g, '-');
  
  // 将日期格式化为更友好的中文格式
  try {
    const fromDate = new Date(from);
    const toDate = new Date(to);
    
    const fromStr = fromDate.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
    
    const toStr = toDate.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
    
    return `${fromStr} 至 ${toStr}`;
  } catch (e) {
    // 如果日期解析失败，直接使用原始字符串
    return `${from} 至 ${to}`;
  }
}

// 定义导出Excel的函数
const exportToExcel = async () => {
  try {
    // 显示加载提示
    $q.loading.show({
      message: t('history.export.loading'),
      spinnerColor: 'secondary',
      backgroundColor: 'dark',
    })

    // 获取所有符合当前过滤条件的记录
    const exportParams = {
      // 使用-1表示不分页，获取所有记录
      page: 1,
      perPage: 100, // 改为100，符合后端API限制
      searchText: filters.searchText || undefined,
      status: filters.status !== '全部' ? filters.status : undefined,
      dateFrom: filters.dateFrom || undefined,
      dateTo: filters.dateTo || undefined
    }

    const response = await detectionService.getDetections(exportParams)
    const exportData = response.items

    if (exportData.length === 0) {
      $q.notify({
        type: 'warning',
        message: t('history.export.noData'),
        position: 'top'
      })
      $q.loading.hide()
      return
    }

    // 准备Excel数据
    const data = exportData.map(record => ({
      [t('history.export.columns.timestamp')]: formatDateTime(record.timestamp),
      [t('history.export.columns.text')]: record.text || '',
      [t('history.export.columns.confidence')]: record.confidence !== null ? `${record.confidence.toFixed(1)}%` : 'N/A',
      [t('history.export.columns.status')]: statusText(record.status),
      [t('history.export.columns.device')]: record.deviceName || '',
      [t('history.export.columns.imageUrl')]: record.imagePath || '',
      [t('history.export.columns.processedImageUrl')]: record.processedImagePath || ''
    }))

    // 创建工作簿
    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '检测历史记录')

    // 设置列宽
    const colWidths = [
      { wch: 20 }, // 检测时间
      { wch: 30 }, // 识别文字
      { wch: 10 }, // 置信度
      { wch: 10 }, // 检测结果
      { wch: 20 }, // 使用设备
      { wch: 30 }, // 图像URL
      { wch: 30 }  // 处理后图像URL
    ]
    ws['!cols'] = colWidths

    // 导出文件
    const fileName = `${t('history.export.fileName')}_${new Date().toISOString().split('T')[0]}.xlsx`
    XLSX.writeFile(wb, fileName)

    $q.notify({
      type: 'positive',
      message: t('history.export.success', { count: data.length }),
      position: 'top',
      timeout: 3000
    })
  } catch (error) {
    console.error('导出失败:', error)
    $q.notify({
      type: 'negative',
      message: t('history.export.failed'),
      position: 'top',
      timeout: 3000
    })
  } finally {
    $q.loading.hide()
  }
}
</script>

<style lang="scss" scoped>
.history-page {
  background: var(--dark-page);
}

.filter-card,
.table-card {
  background: var(--dark-card);
}

.history-table {
  background: transparent;

  :deep(.q-table__card) {
    background: var(--dark-card);
  }

  :deep(.q-table__container) {
    background: transparent;
  }

  :deep(th) {
    font-weight: 500;
    color: var(--q-primary);
  }
}

.image-container {
  width: 100%;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #111;
  border-radius: 4px;
  overflow: hidden;
}

.detection-image {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.no-image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  color: #666;
  font-style: italic;
}
</style>