<template>
  <q-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    persistent
    class="test-panel-dialog"
  >
    <q-card class="test-panel" style="width: 900px; max-width: 90vw">
      <q-card-section class="test-panel-header row items-center q-py-sm">
        <div class="row items-center">
          <q-icon name="account_tree" size="24px" color="info" class="q-mr-sm" />
          <div class="text-h6">流水线测试</div>
        </div>
        <q-space />
        <q-btn-group flat>
          <q-btn :loading="testing" color="primary" icon="play_arrow" label="运行" @click="runTest" />
          <q-btn flat icon="close" @click="emit('update:modelValue', false)">
            <q-tooltip>关闭</q-tooltip>
          </q-btn>
        </q-btn-group>
      </q-card-section>

      <q-card-section class="test-panel-content" style="max-height: 600px">
        <div class="row q-col-gutter-md">
          <!-- 左侧输入面板 -->
          <div class="col-12 col-md-6">
            <q-card flat bordered class="input-panel">
              <q-card-section class="panel-section-header">
                <div class="text-subtitle1">
                  <q-icon name="input" class="q-mr-sm" />
                  输入参数
                </div>
              </q-card-section>
              <q-separator />
              <q-card-section class="panel-section-content">
                <div v-for="param in pipeline.inputParams" :key="param.name" class="param-input q-mb-md">
                  <div class="row items-center q-mb-sm">
                    <div class="text-subtitle2">{{ param.name }}</div>
                    <q-space />
                    <q-chip dense size="sm" :color="getTypeColor(param.type)">
                      {{ param.type }}
                    </q-chip>
                  </div>
                  
                  <!-- 根据参数类型渲染不同的输入控件 -->
                  <div class="param-input-field">
                    <template v-if="param.type === ParamType.TEXT">
                      <q-input
                        v-model="inputValues[param.name]"
                        :placeholder="param.description"
                        outlined
                        dense
                        :rules="[val => !param.required || !!val || '必填项']"
                      />
                    </template>
                    
                    <template v-else-if="param.type === ParamType.NUMBER">
                      <q-input
                        v-model.number="inputValues[param.name]"
                        type="number"
                        :placeholder="param.description"
                        outlined
                        dense
                        :rules="[val => !param.required || val !== null || '必填项']"
                      />
                    </template>
                    
                    <template v-else-if="param.type === ParamType.BOOLEAN">
                      <q-toggle
                        v-model="inputValues[param.name]"
                        :label="param.description"
                      />
                    </template>
                    
                    <template v-else-if="param.type === ParamType.IMAGE">
                      <q-file
                        v-model="inputValues[param.name]"
                        outlined
                        dense
                        accept="image/*"
                        :rules="[val => !param.required || !!val || '必填项']"
                      >
                        <template v-slot:prepend>
                          <q-icon name="attach_file" />
                        </template>
                        <template v-slot:append v-if="inputValues[param.name]">
                          <q-icon name="close" class="cursor-pointer" @click.stop="inputValues[param.name] = null" />
                        </template>
                      </q-file>
                      <q-img
                        v-if="inputValues[param.name]"
                        :src="getImagePreview(inputValues[param.name])"
                        class="q-mt-sm"
                        style="max-height: 200px"
                      />
                    </template>
                    
                    <template v-else-if="param.type === ParamType.ARRAY || param.type === ParamType.OBJECT">
                      <q-input
                        v-model="inputValues[param.name]"
                        type="textarea"
                        :placeholder="param.description + ' (JSON格式)'"
                        outlined
                        dense
                        :rules="[
                          val => !param.required || !!val || '必填项',
                          val => {
                            try {
                              if (val) JSON.parse(val)
                              return true
                            } catch (e) {
                              return '请输入有效的JSON格式'
                            }
                          }
                        ]"
                      />
                    </template>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- 右侧输出面板 -->
          <div class="col-12 col-md-6">
            <q-card flat bordered class="output-panel">
              <q-card-section class="panel-section-header">
                <div class="text-subtitle1">
                  <q-icon name="output" class="q-mr-sm" />
                  输出结果
                </div>
              </q-card-section>
              <q-separator />
              <q-card-section class="panel-section-content">
                <div v-for="param in pipeline.outputParams" :key="param.name" class="param-output q-mb-md">
                  <div class="row items-center q-mb-sm">
                    <div class="text-subtitle2">{{ param.name }}</div>
                    <q-space />
                    <q-chip dense size="sm" :color="getTypeColor(param.type)">
                      {{ param.type }}
                    </q-chip>
                  </div>
                  
                  <!-- 根据参数类型显示不同的输出展示 -->
                  <div class="param-output-field">
                    <template v-if="param.type === ParamType.IMAGE && outputValues[param.name]">
                      <q-img
                        :src="`data:image/png;base64,${outputValues[param.name]}`"
                        class="output-image"
                        style="max-height: 200px; cursor: zoom-in;"
                        @click="openImagePreview(`data:image/png;base64,${outputValues[param.name]}`, param.name)"
                      />
                    </template>
                    <template v-else>
                      <div class="output-value">
                        <pre>{{ formatOutputValue(outputValues[param.name], param.type) }}</pre>
                      </div>
                    </template>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- 执行日志面板 -->
        <q-card flat bordered class="log-panel q-mt-md">
          <q-card-section class="panel-section-header">
            <div class="text-subtitle1">
              <q-icon name="subject" class="q-mr-sm" />
              执行日志
            </div>
            <q-space />
            <q-btn flat dense icon="delete_sweep" @click="clearLogs">
              <q-tooltip>清空日志</q-tooltip>
            </q-btn>
          </q-card-section>
          <q-separator />
          <q-card-section class="panel-section-content log-content">
            <div v-if="logs.length === 0" class="text-grey text-center q-pa-md">
              尚无执行日志，请运行流水线
            </div>
            <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="getLogClass(log.type)">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-type">{{ log.type }}</span>
              
              <!-- 检测并显示 base64 图像 -->
              <template v-if="isBase64Image(log.message)">
                <div class="log-message">
                  <div>图像数据预览</div>
                  <q-img
                    :src="`data:image/png;base64,${log.message.replace(/^data:image\/[a-z]+;base64,/, '')}`"
                    class="log-image-preview"
                    style="max-height: 100px; max-width: 200px; cursor: zoom-in;"
                    @click="openImagePreview(`data:image/png;base64,${log.message.replace(/^data:image\/[a-z]+;base64,/, '')}`, '日志图像')"
                  />
                </div>
              </template>
              <span v-else class="log-message">{{ log.message }}</span>
            </div>
          </q-card-section>
        </q-card>
      </q-card-section>
    </q-card>

    <!-- 添加图片预览对话框 -->
    <q-dialog v-model="imagePreview.show" maximized>
      <q-card class="image-preview-dialog">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">{{ imagePreview.title }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        
        <q-card-section class="image-preview-content">
          <q-img
            :src="imagePreview.src"
            class="full-image"
            fit="contain"
          />
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Pipeline } from '@/services/pipeline'
import { ParamType } from '@/services/cv_operation'
import { pipelineService } from '@/services/pipeline'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const props = defineProps<{
  modelValue: boolean
  pipeline: Partial<Pipeline>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const testing = ref(false)
const inputValues = ref<Record<string, any>>({})
const outputValues = ref<Record<string, any>>({})
const logs = ref<{ time: string, type: string, message: string }[]>([])

// 添加图片预览状态变量
const imagePreview = ref({
  show: false,
  src: '',
  title: ''
})

// 根据参数类型返回不同的颜色
const getTypeColor = (type: ParamType) => {
  const colorMap: Record<string, string> = {
    [ParamType.TEXT]: 'blue-grey',
    [ParamType.NUMBER]: 'deep-orange',
    [ParamType.BOOLEAN]: 'light-blue',
    [ParamType.IMAGE]: 'teal',
    [ParamType.ARRAY]: 'purple',
    [ParamType.OBJECT]: 'brown'
  }
  return colorMap[type] || 'grey'
}

// 获取日志类型对应的样式类
const getLogClass = (type: string) => {
  switch (type) {
    case 'INFO': return 'log-info'
    case 'WARNING': return 'log-warning'
    case 'ERROR': return 'log-error'
    case 'SUCCESS': return 'log-success'
    case 'IMAGE': return 'log-image'
    default: return ''
  }
}

// 获取图片预览URL
const getImagePreview = (file: File) => {
  return URL.createObjectURL(file)
}

// 处理文件上传
const handleFileUpload = async (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const base64Data = reader.result as string
      // 移除 data URL 前缀，只保留 base64 数据
      const base64Content = base64Data.split(',')[1]
      resolve(base64Content)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// 格式化输出值
const formatOutputValue = (value: any, type: string) => {
  if (value === null || value === undefined) return '无数据'
  
  if (type === ParamType.IMAGE) {
    return `[图像数据]` // 图像已在上方显示
  }
  
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2)
  }
  
  return String(value)
}

// 添加检测 base64 图像的函数
const isBase64Image = (str: string) => {
  if (typeof str !== 'string') return false
  
  // 检查是否是有效的 base64 字符串
  const base64Regex = /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/
  const trimmedStr = str.trim().replace(/^data:image\/[a-z]+;base64,/, '')
  
  if (!base64Regex.test(trimmedStr)) return false
  
  // 检查长度是否合理 (至少 100 字符，避免误判)
  return trimmedStr.length > 100
}

// 验证输入参数
const validateInputs = (): boolean => {
  for (const param of props.pipeline.inputParams || []) {
    if (param.required && (inputValues.value[param.name] === undefined || inputValues.value[param.name] === '')) {
      $q.notify({
        type: 'negative',
        message: `${param.name} 是必填项`
      })
      return false
    }
  }
  return true
}

// 准备参数
const prepareParams = async (): Promise<Record<string, any>> => {
  const params: Record<string, any> = {}
  
  for (const param of props.pipeline.inputParams || []) {
    let value = inputValues.value[param.name]
    
    // 处理不同类型的参数
    switch (param.type) {
      case ParamType.IMAGE:
        if (value instanceof File) {
          value = await handleFileUpload(value)
        }
        break
      case ParamType.NUMBER:
        value = value === '' ? null : Number(value)
        break
      case ParamType.BOOLEAN:
        value = Boolean(value)
        break
      case ParamType.ARRAY:
      case ParamType.OBJECT:
        if (typeof value === 'string') {
          try {
            value = JSON.parse(value)
          } catch (e) {
            throw new Error(`${param.name} 的值不是有效的 JSON 格式`)
          }
        }
        break
      case ParamType.TEXT:
        value = value === '' ? null : String(value)
        break
    }
    
    // 只添加非空值
    if (value !== undefined && value !== null) {
      params[param.name] = value
    }
  }
  
  return params
}

// 添加日志条目
const addLog = (type: string, message: string, imageData?: string) => {
  const now = new Date()
  const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  
  logs.value.push({
    time: timeStr,
    type,
    message: imageData || message
  })
  
  // 滚动到日志底部
  nextTick(() => {
    const logContent = document.querySelector('.log-content')
    if (logContent) {
      logContent.scrollTop = logContent.scrollHeight
    }
  })
}

// 清空日志
const clearLogs = () => {
  logs.value = []
}

// 运行测试
const runTest = async () => {
  if (!validateInputs()) return
  
  testing.value = true
  clearLogs()
  outputValues.value = {}
  
  addLog('INFO', '准备执行流水线')
  
  try {
    // 准备参数
    const params = await prepareParams()
    addLog('INFO', `输入参数准备完成: ${Object.keys(params).join(', ')}`)
    
    // 调用API，测试时启用日志
    const result = await pipelineService.applyPipeline(props.pipeline.id!, {
      inputParams: params,
      enableLog: true  // 测试时启用日志
    })
    
    // 处理后端返回的日志
    if (result.logs && Array.isArray(result.logs)) {
      // 添加后端日志
      result.logs.forEach(log => {
        addLog(log.type, log.message)
      })
    }
    
    // 处理结果
    for (const key in result.outputParams) {
      outputValues.value[key] = result.outputParams[key]
      
      // 检查是否是 base64 图像，如果是则添加图像日志
      if (typeof result.outputParams[key] === 'string' && isBase64Image(result.outputParams[key])) {
        addLog('IMAGE', `${key} 图像输出`, result.outputParams[key])
      } else {
        // 对于非图像输出，记录键值对
        addLog('INFO', `输出参数 ${key}: ${JSON.stringify(result.outputParams[key]).substring(0, 100)}${JSON.stringify(result.outputParams[key]).length > 100 ? '...' : ''}`)
      }
    }
    
    addLog('SUCCESS', '流水线执行成功')
  } catch (error: any) {
    console.error('Pipeline execution error:', error)
    
    // 处理错误中的日志
    if (error.response?.data?.detail?.logs && Array.isArray(error.response.data.detail.logs)) {
      error.response.data.detail.logs.forEach(log => {
        addLog(log.type, log.message)
      })
    }
    
    addLog('ERROR', `执行失败: ${error.message || '未知错误'}`)
  } finally {
    testing.value = false
  }
}

// 重置状态
const resetState = () => {
  inputValues.value = {}
  outputValues.value = {}
  
  // 设置默认值
  for (const param of props.pipeline.inputParams || []) {
    if (param.default !== undefined) {
      inputValues.value[param.name] = param.default
    }
  }
}

// 监听对话框关闭时重置状态
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    resetState()
  }
})

// 监听流水线变化
watch(() => props.pipeline, () => {
  if (props.modelValue) {
    resetState()
  }
}, { deep: true })

// 打开图片预览
const openImagePreview = (src: string, title: string) => {
  imagePreview.value = {
    show: true,
    src,
    title
  }
}

// 关闭图片预览
const closeImagePreview = () => {
  imagePreview.value.show = false
}

// 引入nextTick
import { nextTick } from 'vue'
</script>

<style lang="scss" scoped>
.test-panel {
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);

  // 工业风格背景
  background-image: 
    radial-gradient(rgba(0, 0, 0, 0.3) 15%, transparent 16%),
    radial-gradient(rgba(0, 0, 0, 0.3) 15%, transparent 16%);
  background-size: 12px 12px;
  background-position: 0 0, 6px 6px;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.03) 25%,
      transparent 25%,
      transparent 75%,
      rgba(255, 255, 255, 0.03) 75%
    );
    background-size: 24px 24px;
    pointer-events: none;
  }
}

.test-panel-header {
  background: linear-gradient(180deg, var(--dark-card) 0%, var(--dark-card-header) 100%);
  border-bottom: 1px solid var(--border-color);
  padding: 8px 16px;
  z-index: 1;
}

.test-panel-content {
  overflow-y: auto;
  padding: 16px;
}

.input-panel,
.output-panel,
.log-panel {
  background: var(--dark-card);
  border: 1px solid var(--border-color);
  height: 100%;

  .panel-section-header {
    background: linear-gradient(180deg, var(--dark-card) 0%, var(--dark-card-header) 100%);
    padding: 12px 16px;
    display: flex;
    align-items: center;
  }

  .panel-section-content {
    padding: 16px;
  }
}

.param-input,
.param-output {
  background: var(--dark-card-header);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 12px;
  
  &:hover {
    border-color: var(--primary);
    box-shadow: 0 0 8px rgba(25, 118, 210, 0.2);
  }
}

.param-input-field,
.param-output-field {
  background: var(--dark-card);
  border-radius: 4px;
  padding: 8px;
}

.output-value {
  font-family: monospace;
  padding: 8px;
  background: var(--dark-page);
  border-radius: 4px;
  border: 1px solid var(--border-color);
  min-height: 36px;
}

:deep(.q-img) {
  border-radius: 4px;
  border: 1px solid var(--border-color);
  background: var(--dark-page);
}

// 日志面板样式
.log-content {
  max-height: 200px;
  overflow-y: auto;
  font-family: monospace;
  background: var(--dark-page);
  border-radius: 4px;
  padding: 8px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;

    &:hover {
      background: var(--primary);
    }
  }
}

.log-entry {
  padding: 4px 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 150px;
  overflow-y: scroll;
  
  &:last-child {
    border-bottom: none;
  }
  
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;

    &:hover {
      background: var(--primary);
    }
  }
}

.log-time {
  color: #888;
  margin-right: 8px;
}

.log-type {
  font-weight: bold;
  margin-right: 8px;
  padding: 1px 4px;
  border-radius: 2px;
}

.log-message {
  color: #ddd;
  display: block;
  padding-right: 4px;
}

.log-info .log-type {
  background: rgba(25, 118, 210, 0.2);
  color: #90caf9;
}

.log-warning .log-type {
  background: rgba(255, 160, 0, 0.2);
  color: #ffd54f;
}

.log-error .log-type {
  background: rgba(211, 47, 47, 0.2);
  color: #ef9a9a;
}

.log-success .log-type {
  background: rgba(76, 175, 80, 0.2);
  color: #a5d6a7;
}

.log-image .log-type {
  background: rgba(156, 39, 176, 0.2);
  color: #ce93d8;
}

.log-image-preview {
  margin-top: 4px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: #222;
  max-height: 120px;
  object-fit: contain;
}

.image-preview-dialog {
  background: rgba(0, 0, 0, 0.9);
  
  .image-preview-content {
    display: flex;
    justify-content: center;
    align-items: center;
    height: calc(100vh - 50px);
    padding: 0;
  }
  
  .full-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }
}

.output-image, .log-image-preview {
  transition: transform 0.2s;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  }
}
</style> 