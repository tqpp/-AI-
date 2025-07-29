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
          <q-icon name="science" size="24px" color="info" class="q-mr-sm" />
          <div class="text-h6">{{ t('cv.operationTestPanel.title') }}</div>
        </div>
        <q-space />
        <q-btn-group flat>
          <q-btn :loading="testing" color="primary" icon="play_arrow" :label="t('cv.operationTestPanel.actions.run')" @click="runTest" />
          <q-btn flat icon="close" @click="emit('update:modelValue', false)">
            <q-tooltip>{{ t('cv.operationTestPanel.actions.close') }}</q-tooltip>
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
                  {{ t('cv.operationTestPanel.input.title') }}
                </div>
              </q-card-section>
              <q-separator />
              <q-card-section class="panel-section-content">
                <div v-for="param in operation.inputParams" :key="param.name" class="param-input q-mb-md">
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
                        :rules="[val => !param.required || !!val || t('cv.operationTestPanel.validation.required')]"
                      />
                    </template>
                    
                    <template v-else-if="param.type === ParamType.NUMBER">
                      <q-input
                        v-model.number="inputValues[param.name]"
                        type="number"
                        :placeholder="param.description"
                        outlined
                        dense
                        :rules="[val => !param.required || val !== null || t('cv.operationTestPanel.validation.required')]"
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
                        :rules="[val => !param.required || !!val || t('cv.operationTestPanel.validation.required')]"
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
                        :placeholder="param.description + t('cv.operationTestPanel.input.jsonFormat')"
                        outlined
                        dense
                        :rules="[
                          val => !param.required || !!val || t('cv.operationTestPanel.validation.required'),
                          val => {
                            try {
                              if (val) JSON.parse(val)
                              return true
                            } catch (e) {
                              return t('cv.operationTestPanel.validation.invalidJson')
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
                  {{ t('cv.operationTestPanel.output.title') }}
                </div>
              </q-card-section>
              <q-separator />
              <q-card-section class="panel-section-content">
                <div v-for="param in operation.outputParams" :key="param.name" class="param-output q-mb-md">
                  <div class="row items-center q-mb-sm">
                    <div class="text-subtitle2">{{ param.name }}</div>
                    <q-space />
                    <q-chip dense size="sm" :color="getTypeColor(param.type)">
                      {{ param.type }}
                    </q-chip>
                  </div>
                  
                  <!-- 根据参数类型显示不同的输出展示 -->
                  <div class="param-output-field">
                    <template v-if="param.type === ParamType.IMAGE">
                      <q-img
                        v-if="outputValues[param.name]"
                        :src="`data:image/png;base64,${outputValues[param.name]}`"
                        class="output-image q-mt-sm"
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
      </q-card-section>

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
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { CVOperation, ParamType } from '@/services/cv_operation'
import { cvOperationService } from '@/services/cv_operation'
import { useQuasar } from 'quasar'

const { t } = useI18n()
const $q = useQuasar()
const props = defineProps<{
  modelValue: boolean
  operation: CVOperation
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const testing = ref(false)
const inputValues = ref<Record<string, any>>({})
const outputValues = ref<Record<string, any>>({})

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

// 打开图片预览
const openImagePreview = (src: string, title: string) => {
  imagePreview.value = {
    show: true,
    src,
    title
  }
}

// 获取图片预览URL
const getImagePreview = (file: File) => {
  if (!file) return ''
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
const formatOutputValue = (value: any, type: ParamType) => {
  switch (type) {
    case ParamType.OBJECT:
    case ParamType.ARRAY:
      return JSON.stringify(value, null, 2)
    case ParamType.BOOLEAN:
      return value ? 'True' : 'False'
    case ParamType.NUMBER:
      return Number(value).toString()
    default:
      return String(value)
  }
}

// 验证输入参数
const validateInputs = (): boolean => {
  for (const param of props.operation.inputParams || []) {
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
  
  for (const param of props.operation.inputParams || []) {
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

// 运行测试
const runTest = async () => {
  if (!props.operation.id) {
    $q.notify({
      type: 'negative',
      message: '请先保存操作'
    })
    return
  }

  if (!validateInputs()) return

  testing.value = true
  try {
    // 准备参数
    const params = await prepareParams()
    
    // 调用API
    const result = await cvOperationService.applyOperation(props.operation.id, {
      inputParams: params
    })
    
    // 处理结果
    outputValues.value = result

    $q.notify({
      type: 'positive',
      message: '测试运行成功'
    })
  } catch (error) {
    console.error('测试失败:', error)
    $q.notify({
      type: 'negative',
      message: error instanceof Error ? error.message : '测试运行失败'
    })
  } finally {
    testing.value = false
  }
}

// 重置状态
const resetState = () => {
  inputValues.value = {}
  outputValues.value = {}
  
  // 设置默认值
  for (const param of props.operation.inputParams || []) {
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

// 监听操作变化
watch(() => props.operation, () => {
  if (props.modelValue) {
    resetState()
  }
}, { deep: true })
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
.output-panel {
  background: var(--dark-card);
  border: 1px solid var(--border-color);
  height: 100%;

  .panel-section-header {
    background: linear-gradient(180deg, var(--dark-card) 0%, var(--dark-card-header) 100%);
    padding: 12px 16px;
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

.output-image {
  transition: transform 0.2s;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  }
}
</style> 