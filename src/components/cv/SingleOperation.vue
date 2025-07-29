<template>
  <q-page class="cv-operations-page q-pa-md">
    <!-- 顶部工具栏 -->
    <div class="toolbar q-mb-md">
      <div class="row items-center q-col-gutter-md">
        <!-- 左侧按钮组 -->
        <div class="col-auto">
          <div class="row items-center q-gutter-sm">
            <q-btn color="primary" icon="add" :label="t('cv.operation.new')" dense @click="createNewOperation" />
            <q-btn-group flat>
              <q-btn flat dense icon="upload_file" :label="t('cv.operation.import')" @click="importOperations">
                <q-tooltip>{{ t('cv.operation.importTooltip') }}</q-tooltip>
                <input type="file" accept=".xlsx" class="hidden-input" ref="fileInput" @change="handleFileImport" />
              </q-btn>
              <q-btn flat dense icon="download" :label="t('cv.operation.export')" @click="exportOperations">
                <q-tooltip>{{ t('cv.operation.exportTooltip') }}</q-tooltip>
              </q-btn>
            </q-btn-group>
            <q-btn v-if="selected.length > 0" flat dense color="negative" icon="delete_sweep"
              :label="t('cv.operation.deleteSelected', { count: selected.length })" @click="confirmBatchDelete">
              <q-tooltip>{{ t('cv.operation.deleteTooltip') }}</q-tooltip>
            </q-btn>
            <q-chip dense color="grey-7" text-color="white" icon="science" size="sm">
              {{ t('cv.operation.operationCount', { count: operations.length }) }}
            </q-chip>
          </div>
        </div>

        <!-- 右侧搜索框和刷新按钮 -->
        <div class="col">
          <div class="row items-center justify-end">
            <q-input v-model="searchText" :placeholder="t('cv.operation.search')" dense outlined class="search-input"
              style="width: 250px">
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
              <template v-slot:append>
                <q-icon v-if="searchText" name="close" class="cursor-pointer" @click="searchText = ''" />
              </template>
            </q-input>
            <q-btn flat dense icon="refresh" class="q-ml-sm" @click="loadOperations" :loading="loading">
              <q-tooltip>{{ t('cv.operation.refresh') }}</q-tooltip>
            </q-btn>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作列表 -->
    <q-card flat bordered class="operations-card">
      <q-table :rows="filteredOperations" :columns="columns" row-key="id" :loading="loading" class="operations-table"
        :pagination="{ rowsPerPage: 10 }" selection="multiple" v-model:selected="selected">
        <!-- 自定义列 -->
        <template v-slot:body-cell-description="props">
          <q-td :props="props">
            <div class="description-cell">
              {{ props.value || '-' }}
            </div>
          </q-td>
        </template>

        <template v-slot:body-cell-created_at="props">
          <q-td :props="props">
            <q-chip dense size="sm" class="time-chip">
              {{ formatDate(props.value) }}
            </q-chip>
          </q-td>
        </template>

        <template v-slot:body-cell-actions="props">
          <q-td :props="props" class="action-cell">
            <q-btn-group flat>
              <q-btn flat dense icon="edit" @click="editOperation(props.row)">
                <q-tooltip>{{ t('cv.operation.actions.edit') }}</q-tooltip>
              </q-btn>
              <q-btn flat dense icon="play_arrow" color="positive" @click.stop="openTestPanel(props.row)">
                <q-tooltip>{{ t('cv.operation.actions.test') }}</q-tooltip>
              </q-btn>
              <q-btn flat dense icon="delete" color="negative" @click.stop="confirmDelete(props.row)">
                <q-tooltip>{{ t('cv.operation.actions.delete') }}</q-tooltip>
              </q-btn>
            </q-btn-group>
          </q-td>
        </template>
      </q-table>
    </q-card>

    <!-- 使用新的编辑器组件 -->
    <operation-editor v-model="showCreateDialog" :operation="editingOperation" :saving="saving" @submit="handleSubmit"
      @update:operation="handleOperationUpdate" />

    <operation-test-panel v-model="showTestPanel" :operation="editingOperation" />

    <!-- 删除确认对话框 -->
    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="delete" color="negative" text-color="white" />
          <span class="q-ml-sm">{{ deleteDialogMessage }}</span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat :label="t('cv.operation.deleteConfirm.cancel')" color="primary" v-close-popup />
          <q-btn flat :label="t('cv.operation.deleteConfirm.confirm')" color="negative" @click="deleteOperation" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'
import { cvOperationService } from '@/services/cv_operation'
import { CVOperation, CreateCVOperationRequest } from '@/services/cv_operation'
import * as XLSX from 'xlsx'
import OperationEditor from './OperationEditor.vue'
import OperationTestPanel from './OperationTestPanel.vue'

const { t } = useI18n()
const $q = useQuasar()

// 状态变量
const operations = ref<CVOperation[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const saving = ref(false)
const searchText = ref('')
const editingOperation = ref<Partial<CVOperation>>({
  name: '',
  description: '',
  code: '',
  inputParams: [],
  outputParams: []
})
const operationToDelete = ref<CVOperation | null>(null)
const selected = ref<CVOperation[]>([])
const showTestPanel = ref(false)

// 表格列配置
const columns = [
  {
    name: 'selection',
    label: '',
    field: 'selection',
    align: 'center' as const,
    sortable: false
  },
  {
    name: 'name',
    required: true,
    label: t('cv.operation.columns.name'),
    align: 'left' as const,
    field: 'name',
    sortable: true
  },
  {
    name: 'description',
    label: t('cv.operation.columns.description'),
    align: 'left' as const,
    field: 'description'
  },
  {
    name: 'created_at',
    label: t('cv.operation.columns.createdAt'),
    align: 'left' as const,
    field: 'createdAt',
    sortable: true
  },
  {
    name: 'actions',
    label: t('cv.operation.columns.actions'),
    align: 'center' as const,
    field: 'actions'
  }
]

// 计算属性
const filteredOperations = computed(() => {
  if (!searchText.value) return operations.value
  const searchLower = searchText.value.toLowerCase()
  return operations.value.filter(op =>
    op.name.toLowerCase().includes(searchLower) ||
    (op.description?.toLowerCase().includes(searchLower))
  )
})

const deleteDialogMessage = computed(() => {
  if (operationToDelete.value) {
    return t('cv.operation.deleteConfirm.singleMessage', { name: operationToDelete.value.name })
  }
  return t('cv.operation.deleteConfirm.batchMessage', { count: selected.value.length })
})

// 方法
const loadOperations = async () => {
  loading.value = true
  try {
    operations.value = await cvOperationService.getOperations()
  } catch (error) {
    console.error(t('cv.operation.notifications.loadError'), error)
    $q.notify({
      type: 'negative',
      message: t('cv.operation.notifications.loadError')
    })
  } finally {
    loading.value = false
  }
}

// 重置编辑操作
const resetEditingOperation = () => {
  editingOperation.value = {
    name: '',
    description: '',
    code: `def process():
    ###可更改区域###
    return {}`,
    inputParams: [],
    outputParams: []
  }
}

const createNewOperation = () => {
  resetEditingOperation()
  showCreateDialog.value = true
}

const editOperation = (operation: CVOperation) => {
  // Deep clone the operation to avoid reference issues
  editingOperation.value = JSON.parse(JSON.stringify(operation))
  showCreateDialog.value = true
}

const openTestPanel = (operation: CVOperation) => {
  editingOperation.value = JSON.parse(JSON.stringify(operation))
  showTestPanel.value = true
}

const confirmDelete = (operation: CVOperation) => {
  operationToDelete.value = operation
  showDeleteDialog.value = true
}

const confirmBatchDelete = () => {
  operationToDelete.value = null
  showDeleteDialog.value = true
}

const deleteOperation = async () => {
  try {
    if (operationToDelete.value) {
      // 单个删除
      await cvOperationService.deleteOperation(operationToDelete.value.id)
    } else {
      // 批量删除
      for (const operation of selected.value) {
        await cvOperationService.deleteOperation(operation.id)
      }
      selected.value = [] // 清空选中项
    }

    await loadOperations()
    showDeleteDialog.value = false

    $q.notify({
      type: 'positive',
      message: operationToDelete.value ? '删除成功' : '批量删除成功',
      position: 'top',
      timeout: 3000
    })
  } catch (error) {
    console.error('删除失败:', error)
    $q.notify({
      type: 'negative',
      message: '删除失败',
      position: 'top',
      timeout: 3000
    })
  } finally {
    operationToDelete.value = null
  }
}

// 优化提交处理
const handleSubmit = async (operationData: Partial<CVOperation>) => {
  saving.value = true
  try {
    // 验证操作名称
    if (!operationData.name?.trim()) {
      throw new Error(t('cv.operation.validation.nameRequired'))
    }

    if (!operationData.code?.includes('def process(') || !operationData.code?.includes('return {')) {
      throw new Error(t('cv.operation.validation.invalidCode'))
    }

    // 确保inputParams和outputParams存在
    if (!Array.isArray(operationData.inputParams)) {
      operationData.inputParams = []
    }
    if (!Array.isArray(operationData.outputParams)) {
      operationData.outputParams = []
    }

    let savedOperation: CVOperation
    if (editingOperation.value.id) {
      const updateData = {
        ...operationData,
        description: operationData.description || undefined,
        inputParams: operationData.inputParams,
        outputParams: operationData.outputParams
      }
      savedOperation = await cvOperationService.updateOperation(editingOperation.value.id, updateData)
    } else {
      const createData: CreateCVOperationRequest = {
        name: operationData.name,
        code: operationData.code,
        description: operationData.description || undefined,
        inputParams: operationData.inputParams,
        outputParams: operationData.outputParams
      }
      savedOperation = await cvOperationService.createOperation(createData)
    }

    // 更新editingOperation，确保包含新创建的id
    editingOperation.value = savedOperation

    await loadOperations()
    $q.notify({
      type: 'positive',
      message: t('cv.operation.notifications.saveSuccess'),
      position: 'top',
      timeout: 3000
    })
  } catch (error) {
    console.error(t('cv.operation.notifications.saveError'), error)
    $q.notify({
      type: 'negative',
      message: error instanceof Error ? error.message : t('cv.operation.notifications.saveError'),
      position: 'top',
      timeout: 5000
    })
  } finally {
    saving.value = false
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString()
}

// 导入导出功能
const fileInput = ref<HTMLInputElement | null>(null)
const importing = ref(false)

const importOperations = () => {
  fileInput.value?.click()
}

const handleFileImport = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  importing.value = true
  try {
    const file = input.files[0]

    // 检查文件大小
    if (file.size > 10 * 1024 * 1024) { // 10MB
      throw new Error('文件大小不能超过10MB')
    }

    // 检查文件类型
    if (!file.name.endsWith('.xlsx')) {
      throw new Error('只支持.xlsx格式的文件')
    }

    const wb = await readExcelFile(file)
    const ws = wb.Sheets[wb.SheetNames[0]]
    const data = XLSX.utils.sheet_to_json(ws)

    // 验证数据格式
    const requiredFields = ['操作名称', '代码']
    for (const row of data as { [k: string]: any }[]) {
      for (const field of requiredFields) {
        if (!row[field]) {
          throw new Error(`缺少必需字段: ${field}`)
        }
      }
    }

    // 批量导入操作
    const results = {
      success: 0,
      failed: 0,
      errors: [] as string[]
    }

    for (const row of data as { [k: string]: any }[]) {
      try {
        const operation = {
          name: row['操作名称'],
          description: row['描述'] || '',
          code: row['代码'],
          inputParams: parseJsonField(row['输入参数']),
          outputParams: parseJsonField(row['输出参数'])
        }

        // 验证代码格式
        if (!operation.code.includes('def process(') || !operation.code.includes('return {')) {
          throw new Error(t('cv.operation.validation.invalidCode'))
        }

        await cvOperationService.createOperation(operation as CreateCVOperationRequest)
        results.success++
      } catch (error) {
        results.failed++
        results.errors.push(`${t('cv.operation.import.failed', { name: row['操作名称'] })}: ${error instanceof Error ? error.message : t('common.unknownError')}`)
      }
    }

    await loadOperations()

    // 显示导入结果
    if (results.failed > 0) {
      $q.notify({
        type: 'warning',
        message: t('cv.operation.import.partialSuccess', { success: results.success, failed: results.failed }),
        position: 'top',
        timeout: 5000
      })

      // 显示详细错误信息
      $q.dialog({
        title: t('cv.operation.importExport.importErrorDetails'),
        message: results.errors.join('\n'),
        html: true,
        ok: {
          label: t('common.confirm')
        }
      })
    } else {
      $q.notify({
        type: 'positive',
        message: t('cv.operation.notifications.importSuccess', { count: results.success }),
        position: 'top',
        timeout: 3000
      })
    }
  } catch (error) {
    console.error(t('cv.operation.notifications.importError'), error)
    $q.notify({
      type: 'negative',
      message: error instanceof Error ? error.message : t('cv.operation.notifications.importError'),
      position: 'top',
      timeout: 5000
    })
  } finally {
    importing.value = false
    input.value = ''
  }
}

const exportOperations = async () => {
  try {
    // 准备导出数据
    const data = operations.value.map(op => ({
      [t('cv.operation.importExport.exportColumns.name')]: op.name,
      [t('cv.operation.importExport.exportColumns.description')]: op.description || '',
      [t('cv.operation.importExport.exportColumns.code')]: op.code,
      [t('cv.operation.importExport.exportColumns.inputParams')]: JSON.stringify(op.inputParams, null, 2),
      [t('cv.operation.importExport.exportColumns.outputParams')]: JSON.stringify(op.outputParams, null, 2),
      [t('cv.operation.importExport.exportColumns.createdAt')]: formatDate(op.createdAt),
      [t('cv.operation.importExport.exportColumns.updatedAt')]: formatDate(op.updatedAt)
    }))

    // 创建工作簿
    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, t('cv.operation.importExport.exportSheetName'))

    // 导出文件
    XLSX.writeFile(wb, `${t('cv.operation.importExport.exportFileName')}_${new Date().toISOString().split('T')[0]}.xlsx`)

    $q.notify({
      type: 'positive',
      message: t('cv.operation.notifications.exportSuccess', { count: data.length }),
      position: 'top',
      timeout: 3000
    })
  } catch (error) {
    console.error(t('cv.operation.notifications.exportError'), error)
    $q.notify({
      type: 'negative',
      message: t('cv.operation.notifications.exportError'),
      position: 'top',
      timeout: 3000
    })
  }
}

// 辅助函数：解析JSON字段
const parseJsonField = (value: string | undefined): any[] => {
  if (!value) return []
  try {
    return JSON.parse(value)
  } catch (error) {
    console.error('JSON解析失败:', error)
    return []
  }
}

// 辅助函数：读取Excel文件
const readExcelFile = (file: File): Promise<XLSX.WorkBook> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (event) => {
      const data = new Uint8Array(event.target?.result as ArrayBuffer)
      const workbook = XLSX.read(data, { type: 'array' })
      resolve(workbook)
    }
    reader.onerror = (error) => {
      reject(error)
    }
    reader.readAsArrayBuffer(file)
  })
}

// 添加处理操作更新的方法
const handleOperationUpdate = (updatedOperation: Partial<CVOperation>) => {
  editingOperation.value = updatedOperation
}

// 生命周期钩子
onMounted(() => {
  loadOperations()
})

</script>

<style lang="scss" scoped>
// 工业化主题变量
:root {
  --dark-page: #121212;
  --dark-card: #1e1e1e;
  --dark-card-header: #252525;
  --border-color: #2c2c2c;
  --primary: #1976d2;
  --info: #0288d1;
  --warning: #ffa000;
  --negative: #d32f2f;
}

.cv-operations-page {
  background: var(--dark-page);
}

.toolbar {
  background: var(--dark-card);
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.operations-card {
  background: var(--dark-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;

  .operations-table {
    max-height: 600px;
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

    :deep(.q-table tbody tr:hover) {
      background: #2a2a2a;
    }
  }
}

.description-cell {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.time-chip {
  background: rgba(255, 255, 255, 0.05);
  font-family: monospace;
}

.action-cell {
  width: 150px;
}

.hidden-input {
  display: none;
}

// 调整按钮组样式
:deep(.q-btn-group) {
  .q-btn {
    padding: 4px 12px;
    min-height: 36px;
    border-color: var(--border-color);

    .q-icon {
      font-size: 20px;
    }

    &:hover {
      background: var(--dark-card-header);
    }
  }
}

// 调整工具栏内间距
.toolbar {
  .q-gutter-sm>* {
    margin-left: 8px;
    margin-right: 8px;

    &:first-child {
      margin-left: 0;
    }

    &:last-child {
      margin-right: 0;
    }
  }
}

// 参数类型图标样式
:deep(.q-field__prepend) {
  .q-icon {
    font-size: 20px;
    color: var(--q-primary);
  }
}

// 参数类型选项样式
:deep(.q-item__section--avatar) {
  .q-icon {
    font-size: 24px;
    color: var(--q-primary);
  }
}

// 参数配置样式
.params-list {
  .q-list {
    border-radius: 4px;
    background: var(--dark-card-header);

    .q-item {
      min-height: 72px;
      padding: 12px;

      &:hover {
        background: rgba(255, 255, 255, 0.03);
      }
    }
  }

  :deep(.q-field) {
    .q-field__control {
      background: var(--dark-card);
    }
  }

  .q-checkbox {
    margin-left: 8px;
  }

  .q-btn[flat] {
    &.q-btn--round {
      opacity: 0.7;

      &:hover {
        opacity: 1;
      }
    }
  }
}

// 调整响应式布局
@media (max-width: 599px) {
  .params-list {
    .q-item {
      .row>div {
        margin-bottom: 8px;

        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }
}

.q-expansion-item {
  :deep(.q-expansion-item__container) {
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;

    .q-expansion-item__header {
      padding: 8px 16px;
      background: var(--dark-card-header);
    }
  }
}

.q-tabs {
  background: var(--dark-card-header);
}
</style>