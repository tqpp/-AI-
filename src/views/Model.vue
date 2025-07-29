<template>
  <q-page class="model-page q-pa-md">
    <div class="row q-col-gutter-md" style="display: flex; flex-wrap: wrap; flex-grow: 1;">
      <!-- 模型列表 -->
      <div class="col-12 col-lg-4">
        <q-card class="model-card">
          <q-card-section>
            <div class="text-h6">{{ t('model.list.title') }}</div>
            <q-list separator>
              <q-item v-for="model in models" :key="model.id" clickable v-ripple @click="selectModel(model)" 
                :class="{ 'model-selected': selectedModel?.id === model.id }">
                <q-item-section avatar>
                  <q-icon name="model_training" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ model.name }} 
                    <q-badge 
                      outline 
                      size="xs" 
                      class="model-id-badge cursor-pointer"
                      @click.stop="copyModelId(model.id, $event)"
                    >
                      ID: {{ model.id }}
                    </q-badge>
                  </q-item-label>
                  <q-item-label caption>{{ t('model.list.architecture') }}: {{ getArchitectureLabel(model.architecture) }}</q-item-label>
                  <q-chip 
                    size="sm" 
                    :color="getStatusColor(model.status)" 
                    text-color="white" 
                    class="q-mt-xs"
                  >
                    {{ getStatusText(model.status) }}
                  </q-chip>
                </q-item-section>
                <q-item-section side>
                  <div class="row q-gutter-xs">
                    <q-btn 
                      v-if="model.status === ModelStatus.COMPLETED" 
                      flat 
                      dense 
                      round 
                      icon="science" 
                      color="info"
                      @click.stop="testModelAction(model)"
                      :title="t('model.list.actions.test')"
                    />
                    <q-btn 
                      v-if="model.status === ModelStatus.NOT_STARTED || model.status === ModelStatus.FAILED" 
                      flat 
                      dense 
                      round 
                      icon="play_arrow" 
                      color="positive"
                      @click.stop="trainModel(model)"
                      :title="t('model.list.actions.train')"
                    />
                    <q-btn 
                      flat 
                      dense 
                      round 
                      icon="delete" 
                      color="negative"
                      @click.stop="confirmDeleteModel(model)"
                      :title="t('model.list.actions.delete')"
                    />
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
            <div v-if="models.length === 0" class="q-py-md text-center text-grey">
              {{ t('model.list.empty') }}
            </div>
            <q-btn
              color="primary"
              icon="add"
              :label="t('model.list.create')"
              class="full-width q-mt-md"
              @click="createModelDialog = true"
            />
          </q-card-section>
        </q-card>
      </div>

      <!-- 训练配置 -->
      <div class="col-12 col-lg-8" v-if="selectedModel">
        <q-card class="mode-switch-card q-mb-md">
          <q-card-section class="q-py-sm">
            <q-btn-toggle
              v-model="activeMode"
              toggle-color="primary"
              color="grey-9"
              text-color="white"
              class="full-width"
              :options="[
                {label: t('model.training.modes.config'), value: 'config', icon: 'tune'},
                {label: t('model.training.modes.test'), value: 'test', icon: 'science', disable: selectedModel?.status !== ModelStatus.COMPLETED},
                {label: t('model.training.modes.logs'), value: 'logs', icon: 'terminal', disable: selectedModel?.status !== ModelStatus.TRAINING},
                {label: t('model.training.modes.files'), value: 'files', icon: 'folder', disable: selectedModel?.status !== ModelStatus.COMPLETED && selectedModel?.status !== ModelStatus.TRAINING}
              ]"
            />
          </q-card-section>
        </q-card>
        
        <!-- 训练配置模式 -->
        <div v-if="activeMode === 'config'">
        <q-card class="training-card">
          <q-card-section>
              <div class="text-h6">{{ selectedModel.name }} 
                <q-badge 
                  color="info" 
                  outline 
                  class="model-id-badge cursor-pointer"
                  @click="copyModelId(selectedModel.id, $event)"
                >
                  ID: {{ selectedModel.id }}
                </q-badge> 
                {{ t('model.training.title') }}</div>
            <div class="row q-col-gutter-md q-mt-md">
              <div class="col-12 col-md-6">
                <q-select
                  outlined
                  v-model="selectedDataset"
                  :options="datasets"
                  option-value="id"
                  option-label="name"
                  :label="t('model.training.params.dataset')"
                  class="full-width"
                  disable
                />
              </div>
              <div class="col-12 col-md-6">
                <q-select
                  outlined
                  v-model="selectedModel.architecture"
                  :options="architectureOptions"
                  :label="t('model.training.params.architecture')"
                  class="full-width"
                  disable
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  outlined
                  v-model.number="epochs"
                  type="number"
                  :label="t('model.training.params.epochs')"
                  class="full-width"
                  :disable="selectedModel.status === ModelStatus.TRAINING"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  outlined
                  v-model.number="batchSize"
                  type="number"
                  :label="t('model.training.params.batchSize')"
                  class="full-width"
                  :disable="selectedModel.status === ModelStatus.TRAINING"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  outlined
                  v-model.number="imgSize"
                  type="number"
                  :label="t('model.training.params.imgSize')"
                  class="full-width"
                  :disable="selectedModel.status === ModelStatus.TRAINING"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  outlined
                  v-model.number="confThres"
                  type="number"
                  :label="t('model.training.params.confThres')"
                  step="0.05"
                  min="0"
                  max="1"
                  class="full-width"
                  :disable="selectedModel.status === ModelStatus.TRAINING"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  outlined
                  v-model.number="iouThres"
                  type="number"
                  :label="t('model.training.params.iouThres')"
                  step="0.05"
                  min="0"
                  max="1"
                  class="full-width"
                  :disable="selectedModel.status === ModelStatus.TRAINING"
                />
              </div>
            </div>
            <q-btn
              color="primary"
              icon="play_arrow"
              :label="selectedModel.status === ModelStatus.TRAINING ? t('model.training.actions.training') : t('model.training.actions.startTraining')"
              class="q-mt-lg"
              @click="startTraining"
              :loading="selectedModel.status === ModelStatus.TRAINING"
              :disable="selectedModel.status === ModelStatus.TRAINING"
            />
          </q-card-section>
        </q-card>

        <!-- 训练进度 -->
          <q-card class="progress-card q-mt-md" v-if="selectedModel">
          <q-card-section>
              <div class="row justify-between items-center">
            <div class="text-h6">{{ t('model.progress.title') }}
              <q-badge 
                color="info" 
                outline 
                class="model-id-badge cursor-pointer"
                @click="copyModelId(selectedModel.id, $event)"
              >
                ID: {{ selectedModel.id }}
              </q-badge>
              </div>
                <q-chip 
                  size="sm" 
                  :color="getProgressColor()" 
                  text-color="white"
                  class="q-ml-sm"
                >
                  {{ getStatusText(selectedModel.status) }}
                </q-chip>
              </div>
              
              <div class="q-mt-md progress-container">
                <!-- 进度条和百分比 -->
                <div class="row items-center q-mb-md">
                  <div class="col-auto progress-label">{{ getProgressText() }}</div>
                  <div class="col q-px-md">
              <q-linear-progress
                rounded
                      size="14px"
                      track-color="grey-8"
                      :value="getProgress()"
                      :color="getProgressColor()"
                      :stripe="selectedModel.status === ModelStatus.TRAINING"
                      :indeterminate="selectedModel.status === ModelStatus.TRAINING && !selectedModel.metrics?.progress"
                      class="progress-bar"
                    />
                  </div>
                  <div class="col-auto progress-value">{{ Math.round(getProgress() * 100) }}%</div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        
        <!-- 模型测试模式 -->
        <div v-else-if="activeMode === 'test' && selectedModel.status === ModelStatus.COMPLETED">
          <ModelTester :selectedModel="selectedModel" />
        </div>
        
        <!-- 训练日志模式 -->
        <div v-else-if="activeMode === 'logs' && selectedModel.status === ModelStatus.TRAINING">
          <q-card class="training-card">
            <q-card-section>
              <div class="row justify-between items-center">
                <div class="text-h6">{{ t('model.logs.title') }}
                  <q-badge 
                    color="info" 
                    outline 
                    class="model-id-badge cursor-pointer"
                    @click="copyModelId(selectedModel.id, $event)"
                  >
                    ID: {{ selectedModel.id }}
                  </q-badge>
                </div>
                <div class="row q-gutter-xs">
                  <q-btn flat dense icon="refresh" color="primary" @click="fetchModelLogs" :title="t('model.logs.actions.refresh')" />
                  <q-btn flat dense icon="content_copy" color="primary" @click="copyLogs" :disable="logs.length === 0" :title="t('model.logs.actions.copy')" />
                  <q-btn flat dense icon="vertical_align_bottom" color="primary" @click="scrollLogsToBottom" :disable="logs.length === 0" :title="t('model.logs.actions.scrollToBottom')" />
                </div>
              </div>
              
              <div ref="terminalContainer" class="terminal-container q-mt-md" style="height: 500px; border-radius: 4px; overflow: hidden;"></div>
            </q-card-section>
          </q-card>
        </div>
        
        <!-- 训练文件模式 -->
        <div v-else-if="activeMode === 'files' && (selectedModel.status === ModelStatus.COMPLETED || selectedModel.status === ModelStatus.TRAINING)">
          <q-card class="files-card">
            <q-card-section>
              <div class="row justify-between items-center">
                <div class="text-h6">{{ t('model.files.title') }}
                  <q-badge 
                    color="info" 
                    outline 
                    class="model-id-badge cursor-pointer"
                    @click="copyModelId(selectedModel.id, $event)"
                  >
                    ID: {{ selectedModel.id }}
                  </q-badge>
                </div>
                <div class="row q-gutter-xs">
                  <q-btn flat dense icon="refresh" color="primary" @click="fetchModelFiles" :title="t('model.files.actions.refresh')" />
                  <q-btn flat dense icon="home" color="primary" @click="navigateToRoot" :title="t('model.files.actions.root')" />
                </div>
              </div>
              
              <q-breadcrumbs class="q-mt-sm" separator="/" active-color="primary">
                <q-breadcrumbs-el :label="t('model.files.actions.root')" icon="home" @click="navigateToRoot" />
                <q-breadcrumbs-el 
                  v-for="(segment, index) in pathSegments" 
                  :key="index"
                  :label="segment"
                  @click="navigateToPath(index)"
                />
              </q-breadcrumbs>
              
              <q-list bordered separator class="rounded-borders q-mt-md">
                <q-item v-if="currentPath !== ''" clickable @click="navigateUp">
                  <q-item-section avatar>
                    <q-icon name="arrow_upward" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ t('model.files.actions.upLevel') }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item v-for="(file, index) in modelFiles" :key="index" clickable @click="handleFileClick(file)">
                  <q-item-section avatar>
                    <q-icon :name="getFileIcon(file)" :color="getFileColor(file)" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ file.name }}</q-item-label>
                    <q-item-label caption>
                      {{ file.isDir ? '目录' : formatFileSize(file.size) }} | {{ formatModifiedTime(file.modifiedTime) }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side v-if="!file.isDir && isPreviewable(file.name)">
                    <q-btn flat dense round icon="visibility" color="primary" @click.stop="openPreview(file)" />
                  </q-item-section>
                </q-item>
                
                <q-item v-if="modelFiles.length === 0">
                  <q-item-section>
                    <q-item-label class="text-center text-grey">{{ t('model.files.empty') }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
          
          <!-- 文件预览对话框 -->
          <q-dialog v-model="previewDialog" maximized persistent>
            <q-card>
              <q-card-section class="row items-center">
                <div class="text-h6">{{ previewFile?.name }}</div>
                <q-space />
                <q-btn icon="close" flat round dense v-close-popup />
              </q-card-section>
              
              <q-separator />
              
              <q-card-section class="file-preview-container">
                <div v-if="isImageFile(previewFile?.name)" class="image-preview">
                  <img :src="previewUrl" alt="文件预览" style="max-width: 100%; max-height: 80vh;" />
                </div>
                <div v-else-if="isTextFile(previewFile?.name)" class="text-preview">
                  <pre class="text-content">{{ previewContent }}</pre>
                </div>
                <div v-else class="unknown-preview">
                  <q-icon name="insert_drive_file" size="6rem" color="grey" />
                  <div class="text-subtitle1 q-mt-md">{{ t('model.files.preview.unsupported') }}</div>
            </div>
          </q-card-section>
              
              <q-card-actions align="right">
                <q-btn flat :label="t('model.files.preview.actions.download')" color="primary" @click="downloadSelectedFile()" icon="download" />
                <q-btn flat :label="t('model.files.preview.actions.close')" color="primary" v-close-popup />
              </q-card-actions>
        </q-card>
          </q-dialog>
      </div>
        
        <!-- 无选中模型时的空状态 -->
        <div v-else>
          <q-card class="training-card flex-center">
            <q-card-section class="text-center">
              <q-icon name="model_training" size="5rem" color="grey-7" />
              <div class="text-h6 q-mt-md">
                <template v-if="activeMode === 'test' && selectedModel?.status !== ModelStatus.COMPLETED">
                  此模型未完成训练，无法进行测试
                </template>
                <template v-else-if="activeMode === 'logs' && selectedModel?.status !== ModelStatus.TRAINING">
                  模型当前未处于训练状态，没有训练日志
                </template>
                <template v-else>
                  请选择功能或操作
                </template>
    </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
      
      <!-- 无选中模型时的空状态 -->
      <div class="col-12 col-lg-8" v-else>
        <q-card class="training-card flex-center">
          <q-card-section class="text-center">
            <q-icon name="model_training" size="5rem" color="grey-7" />
            <div class="text-h6 q-mt-md">{{ t('model.status.empty') }}</div>
            <div class="text-subtitle1 q-mt-sm text-grey-7">
              {{ t('model.status.emptyHint') }}
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
    
    <!-- 新建模型对话框 -->
    <q-dialog v-model="createModelDialog" persistent>
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">{{ t('model.dialogs.create.title') }}</div>
        </q-card-section>
        
        <q-card-section class="q-pt-none">
          <q-input 
            outlined 
            v-model="newModel.name" 
            :label="t('model.dialogs.create.name')" 
            autofocus
            :rules="[val => !!val || t('model.dialogs.create.nameRequired')]"
          />
          
          <q-select
            outlined
            v-model="newModel.dataset_id"
            :options="datasets"
            option-value="id"
            option-label="name"
            :label="t('model.dialogs.create.dataset')"
            class="q-mt-md"
            :rules="[val => !!val || t('model.dialogs.create.datasetRequired')]"
            emit-value
            map-options
          />
          
          <q-select
            outlined
            v-model="newModel.architecture"
            :options="architectureOptions.map(opt => opt.value)"
            :option-label="getArchitectureLabel"
            :label="t('model.training.params.architecture')"
            class="q-mt-md"
          />
          
          <q-input 
            outlined 
            v-model.number="newModel.parameters!.epochs" 
            type="number"
            :label="t('model.training.params.epochs')"
            class="q-mt-md"
          />
          
          <q-input 
            outlined 
            v-model.number="newModel.parameters!.batch_size" 
            type="number"
            :label="t('model.training.params.batchSize')"
            class="q-mt-md"
          />
          
          <q-input 
            outlined 
            v-model.number="newModel.parameters!.img_size" 
            type="number"
            :label="t('model.training.params.imgSize')"
            class="q-mt-md"
          />
          
          <q-input 
            outlined 
            v-model.number="newModel.parameters!.conf_thres" 
            type="number"
            :label="t('model.training.params.confThres')"
            step="0.05"
            min="0"
            max="1"
            class="q-mt-md"
          />
          
          <q-input 
            outlined 
            v-model.number="newModel.parameters!.iou_thres" 
            type="number"
            :label="t('model.training.params.iouThres')"
            step="0.05"
            min="0"
            max="1"
            class="q-mt-md"
          />
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat :label="t('common.cancel')" color="primary" v-close-popup />
          <q-btn flat :label="t('common.confirm')" color="primary" @click="createModel" />
        </q-card-actions>
      </q-card>
    </q-dialog>
    
    <!-- 删除确认对话框 -->
    <q-dialog v-model="deleteConfirmDialog">
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="delete" color="negative" text-color="white" />
          <span class="q-ml-sm">{{ t('model.dialogs.delete.message', { name: modelToDelete?.name }) }}</span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat :label="t('common.cancel')" color="primary" v-close-popup />
          <q-btn flat :label="t('common.delete')" color="negative" @click="deleteModel" :loading="deleting" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'
import { modelService, Model, ModelStatus, ModelArchitecture, CreateModelRequest, ModelFile } from '../services/model'
import { useRouter, useRoute } from 'vue-router'
import { AnnotationService } from '../services/annotation'
import ModelTester from '../components/model/ModelTester.vue'
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'

const { t } = useI18n()
const $q = useQuasar()
const router = useRouter()
const route = useRoute()
const annotationService = new AnnotationService()

// 数据集列表
const datasets = ref<any[]>([]) 

// 模型列表
const models = ref<Model[]>([])
const selectedModel = ref<Model | null>(null)
const createModelDialog = ref(false)
const deleteConfirmDialog = ref(false)
const modelToDelete = ref<Model | null>(null)
const creating = ref(false)
const deleting = ref(false)
const polling = ref<number | null>(null)

// 组件显示模式
const activeMode = ref<'config' | 'test' | 'logs' | 'files'>('config')

// 路由参数处理
const props = defineProps({
  mode: {
    type: String,
    default: 'config'
  },
  modelId: {
    type: Number,
    default: null
  }
})

// 模型架构选项
const architectureOptions = [
  { value: ModelArchitecture.YOLO_V5, label: 'YOLO v5' },
  { value: ModelArchitecture.YOLO_V8, label: 'YOLO v8' },
  { value: ModelArchitecture.YOLO_V9, label: 'YOLO v9' }
]

// 新模型表单
const newModel = ref<CreateModelRequest>({
  name: '',
  architecture: ModelArchitecture.YOLO_V8,  // 默认使用YOLOv8
  dataset_id: undefined,
  parameters: {
    epochs: 50,
    batch_size: 16,
    img_size: 640,
    conf_thres: 0.25,
    iou_thres: 0.45
  }
})

// 训练参数
const epochs = ref(50)
const batchSize = ref(16)
const imgSize = ref(640)
const confThres = ref(0.25)
const iouThres = ref(0.45)

// 获取选中的数据集
const selectedDataset = computed(() => {
  if (!selectedModel.value?.dataset_id) return null
  return datasets.value.find(d => d.id === selectedModel.value?.dataset_id) || null
})

// 验证新模型表单
const isNewModelValid = computed(() => {
  return !!(
    newModel.value.name && 
    newModel.value.architecture && 
    newModel.value.dataset_id
  )
})

// 获取架构标签
const getArchitectureLabel = (arch: ModelArchitecture) => {
  const option = architectureOptions.find(opt => opt.value === arch)
  return option ? option.label : arch
}

// 获取状态文本
const getStatusText = (status: ModelStatus) => {
  switch (status) {
    case ModelStatus.NOT_STARTED:
      return '未开始'
    case ModelStatus.TRAINING:
      return '训练中'
    case ModelStatus.COMPLETED:
      return '已完成'
    case ModelStatus.FAILED:
      return '失败'
    default:
      return status
  }
}

// 获取进度文本
const getProgressText = () => {
  if (!selectedModel.value) return '0%'
  
  if (selectedModel.value.status === ModelStatus.NOT_STARTED) {
    return '0%'
  } else if (selectedModel.value.status === ModelStatus.COMPLETED) {
    return '100%'
  } else if (selectedModel.value.status === ModelStatus.FAILED) {
    return '失败'
  } else if (selectedModel.value.metrics?.progress !== undefined) {
    return `${Math.round(selectedModel.value.metrics.progress * 100)}%`
  } else {
    // 更友好的进行中提示
    const dots = Math.floor(Date.now() / 500) % 4; // 动态显示点的数量
    return `训练中${''.padEnd(dots, '.')}`;
  }
}

// 获取进度值
const getProgress = () => {
  if (!selectedModel.value) return 0
  
  if (selectedModel.value.status === ModelStatus.COMPLETED) {
    return 1
  } else if (selectedModel.value.metrics?.progress !== undefined) {
    return selectedModel.value.metrics.progress
  } else if (selectedModel.value.status === ModelStatus.TRAINING) {
    return 0.5 // 中间状态
  }
  
  return 0
}

// 获取进度条颜色
const getProgressColor = (status: ModelStatus = ModelStatus.NOT_STARTED) => {
  if (!selectedModel.value) return 'primary'
  
  const statusToCheck = status || (selectedModel.value ? selectedModel.value.status : ModelStatus.NOT_STARTED)
  
  switch (statusToCheck) {
    case ModelStatus.TRAINING:
      return 'info'
    case ModelStatus.COMPLETED:
      return 'positive'
    case ModelStatus.FAILED:
      return 'negative'
    default:
      return 'primary'
  }
}

// 开始训练模型
const startTraining = async () => {
  if (!selectedModel.value) return
  
  try {
    await updateModelParameters()
    await modelService.startTraining(selectedModel.value.id)
    await refreshModel(selectedModel.value.id)
    
    $q.notify({
      type: 'positive',
      message: t('model.notifications.trainStarted'),
      position: 'top',
    })
    
    startPolling()
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: t('model.notifications.trainFailed', { error: (error as Error).message }),
      position: 'top',
    })
  }
}

// 更新模型参数
const updateModelParameters = async () => {
  if (!selectedModel.value) return
  
  try {
    await modelService.updateModel(selectedModel.value.id, {
      parameters: {
        epochs: epochs.value,
        batch_size: batchSize.value,
        img_size: imgSize.value,
        conf_thres: confThres.value,
        iou_thres: iouThres.value
      }
    })
  } catch (error) {
    throw new Error(t('model.notifications.updateParamsFailed', { error: (error as Error).message }))
  }
}

// 选择模型
const selectModel = (model: Model) => {
  selectedModel.value = model
  
  // 更新训练参数
  epochs.value = model.parameters.epochs || 50
  batchSize.value = model.parameters.batch_size || 16
  imgSize.value = model.parameters.img_size || 640
  confThres.value = model.parameters.conf_thres || 0.25
  iouThres.value = model.parameters.iou_thres || 0.45
  
  // 如果模型正在训练，获取日志并开始轮询状态
  if (model.status === ModelStatus.TRAINING) {
    fetchModelLogs()
    startPolling()
  }
}

// 创建新模型
const createModel = async () => {
  try {
    if (!newModel.value.name) {
      $q.notify({
        type: 'warning',
        message: t('model.dialogs.create.nameRequired'),
        position: 'top'
      })
      return
    }
    
    if (!newModel.value.dataset_id) {
      $q.notify({
        type: 'warning',
        message: t('model.dialogs.create.datasetRequired'),
        position: 'top'
      })
      return
    }
    
    const model = await modelService.createModel(newModel.value)
    models.value.push(model)
    
    newModel.value = {
      name: '',
      architecture: ModelArchitecture.YOLO_V8,
      dataset_id: undefined,
      parameters: {
        epochs: 50,
        batch_size: 16,
        img_size: 640,
        conf_thres: 0.25,
        iou_thres: 0.45
      }
    }
    
    createModelDialog.value = false
    
    $q.notify({
      type: 'positive',
      message: t('model.notifications.createSuccess'),
      position: 'top'
    })
    
    selectModel(model)
  } catch (error) {
    console.error('Failed to create model:', error)
    $q.notify({
      type: 'negative',
      message: t('model.notifications.createFailed', { error: (error as Error).message }),
      position: 'top'
    })
  }
}

// 确认删除模型
const confirmDeleteModel = (model: Model) => {
  modelToDelete.value = model
  deleteConfirmDialog.value = true
}

// 删除模型
const deleteModel = async () => {
  if (!modelToDelete.value) return
  
  deleting.value = true
  
  try {
    await modelService.deleteModel(modelToDelete.value.id)
    
    // 从列表中移除
    models.value = models.value.filter(m => m.id !== modelToDelete.value?.id)
    
    // 如果删除的是当前选中的模型，清空选中
    if (selectedModel.value?.id === modelToDelete.value.id) {
      selectedModel.value = null
    }
    
    deleteConfirmDialog.value = false
    
    $q.notify({
      type: 'positive',
      message: t('model.notifications.deleteSuccess'),
      position: 'top',
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: t('model.notifications.deleteFailed', { error: (error as Error).message }),
      position: 'top',
    })
  } finally {
    deleting.value = false
    modelToDelete.value = null
  }
}

// 导出模型
const exportModel = async (model: Model) => {
  try {
    const result = await modelService.exportModel(model.id)
    
    $q.notify({
      type: 'positive',
      message: `模型导出成功: ${result.file_path}`,
      position: 'top',
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: `导出模型失败: ${(error as Error).message}`,
      position: 'top',
    })
  }
}

// 训练模型
const trainModel = (model: Model) => {
  selectModel(model)
  startTraining()
}

// 刷新模型数据
const refreshModel = async (modelId: number) => {
  try {
    const model = await modelService.getModel(modelId)
    
    // 更新模型列表
    const index = models.value.findIndex(m => m.id === modelId)
    if (index !== -1) {
      models.value[index] = model
    }
    
    // 更新选中的模型
    if (selectedModel.value?.id === modelId) {
      selectedModel.value = model
    }
    
    // 如果模型正在训练中，获取训练日志
    if (model.status === ModelStatus.TRAINING) {
      await fetchModelLogs()
    }
  } catch (error) {
    console.error('Failed to refresh model:', error)
  }
}

// 开始轮询训练状态
const startPolling = () => {
  // 停止之前的轮询
  stopPolling()
  
  // 开始新的轮询
  polling.value = window.setInterval(async () => {
    if (!selectedModel.value) {
      stopPolling()
      return
    }
    
    // 更新模型信息
    await refreshModel(selectedModel.value.id)
    
    // 如果训练已完成或失败，停止轮询
    if (selectedModel.value.status !== ModelStatus.TRAINING) {
      stopPolling()
    }
  }, 2000) // 每2秒轮询一次
}

// 停止轮询
const stopPolling = () => {
  if (polling.value !== null) {
    window.clearInterval(polling.value)
    polling.value = null
  }
}

// 加载数据集
const loadDatasets = async () => {
  try {
    const response = await annotationService.getDatasets()
    datasets.value = response
  } catch (error) {
    console.error('Failed to load datasets:', error)
    $q.notify({
      type: 'negative',
      message: t('model.notifications.loadDatasetsFailed'),
      position: 'top',
    })
  }
}

// 格式化时间
const formatTime = (timestamp: string | number) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString()
}

// 格式化持续时间
const formatDuration = (seconds: number) => {
  if (seconds === undefined || seconds === null) return '-'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  const parts = []
  if (hours > 0) parts.push(`${hours}小时`)
  if (minutes > 0) parts.push(`${minutes}分钟`)
  if (secs > 0 || parts.length === 0) parts.push(`${secs}秒`)
  
  return parts.join(' ')
}

// 测试模型操作
const testModelAction = (model: Model) => {
  selectModel(model)
  activeMode.value = 'test'
}

// 获取状态颜色
const getStatusColor = (status: ModelStatus) => {
  switch (status) {
    case ModelStatus.TRAINING:
      return 'blue'
    case ModelStatus.COMPLETED:
      return 'positive'
    case ModelStatus.FAILED:
      return 'negative'
    default:
      return 'grey'
  }
}

// 添加日志相关变量和方法
const logs = ref<string[]>([])
const terminalContainer = ref(null)
let terminal: Terminal | null = null
let fitAddon: any = null
let lastEpochLine = ''
let lastBatchLine = ''
let lastProgressLine = ''

// 初始化xterm终端
const initTerminal = () => {
  if (terminal) return
  
  // 确保DOM元素已加载
  if (!terminalContainer.value) return
  
  terminal = new Terminal({
    cursorBlink: false,
    fontFamily: 'Menlo, Monaco, "Courier New", monospace',
    fontSize: 13,
    lineHeight: 1.2,
    theme: {
      background: '#1e1e1e',
      foreground: '#e6e6e6',
      black: '#000000',
      red: '#ff5555',
      green: '#50fa7b',
      yellow: '#f1fa8c',
      blue: '#bd93f9',
      magenta: '#ff79c6',
      cyan: '#8be9fd',
      white: '#f8f8f2',
      brightBlack: '#6272a4',
      brightRed: '#ff6e6e',
      brightGreen: '#69ff94',
      brightYellow: '#ffffa5',
      brightBlue: '#d6acff',
      brightMagenta: '#ff92df',
      brightCyan: '#a4ffff',
      brightWhite: '#ffffff'
    },
    scrollback: 5000,
    convertEol: true
  })
  
  fitAddon = new FitAddon()
  terminal.loadAddon(fitAddon)
  terminal.open(terminalContainer.value)
  fitAddon.fit()
  
  // 监听窗口大小变化以调整终端大小
  window.addEventListener('resize', () => {
    if (fitAddon) fitAddon.fit()
  })
  
  // 如果有历史日志，立即显示
  if (logs.value.length > 0) {
    updateTerminal(logs.value)
  }
}

// 获取模型日志的方法
const fetchModelLogs = async () => {
  if (!selectedModel.value) return
  
  try {
    const response = await modelService.getModelLogs(selectedModel.value.id)
    logs.value = response.logs
    
    // 更新终端显示
    if (terminal) {
      updateTerminal(logs.value)
    }
    
    // 自动滚动到底部
    nextTick(() => {
      if (logs.value.length > 0 && terminal) {
        terminal.scrollToBottom()
      }
    })
  } catch (error) {
    console.error('Failed to fetch model logs:', error)
  }
}

// 更新终端显示
const updateTerminal = (newLogs: string[]) => {
  if (!terminal) return
  
  // 清空终端
  terminal.clear()
  
  // 分析并显示日志
  let epochLine = -1
  let batchLine = -1
  let progressLine = -1
  let otherLines: string[] = []
  
  newLogs.forEach((log, index) => {
    // 识别不同类型的日志行
    const isEpochInfo = /epoch\s+\d+\/\d+/i.test(log) || 
                       /epoch\s+\[\s*\d+\/\s*\d+\]/i.test(log) ||
                       (log.includes('epoch') && log.includes('%'))
                       
    const isBatchInfo = /batch\s+\d+\/\d+/i.test(log) || 
                       /\d+\/\d+\s+batch/i.test(log) ||
                       (log.includes('batch') && log.includes('%'))
                       
    const isProgressInfo = log.includes('%') && 
                          (log.includes('progress') || 
                           log.includes('ETA') || 
                           log.includes('training'))
                           
    // 记录最新位置
    if (isEpochInfo) {
      epochLine = index
      lastEpochLine = log
    } else if (isBatchInfo) {
      batchLine = index
      lastBatchLine = log
    } else if (isProgressInfo) {
      progressLine = index
      lastProgressLine = log
    } else {
      otherLines.push(log)
    }
  })
  
  // 首先显示普通日志行
  otherLines.forEach(line => {
    if (!terminal) return
    
    if (line.toLowerCase().includes('error') || line.toLowerCase().includes('exception')) {
      terminal.writeln(`\x1b[31m${line}\x1b[0m`) // 红色
    } else if (line.toLowerCase().includes('warning') || line.toLowerCase().includes('warn')) {
      terminal.writeln(`\x1b[33m${line}\x1b[0m`) // 黄色
    } else if (line.toLowerCase().includes('info') || line.includes('[INFO]')) {
      terminal.writeln(`\x1b[36m${line}\x1b[0m`) // 青色
    } else if (line.includes('[系统]')) {
      terminal.writeln(`\x1b[32m${line}\x1b[0m`) // 绿色
    } else {
      terminal.writeln(line)
    }
  })
  
  // 添加一行分隔
  if ((lastEpochLine || lastBatchLine || lastProgressLine) && otherLines.length > 0 && terminal) {
    terminal.writeln('\r\n\x1b[90m-------------- 训练进度 --------------\x1b[0m\r\n')
  }
  
  // 然后显示进度信息
  if (lastEpochLine && terminal) {
    terminal.writeln(`\x1b[1;96m${lastEpochLine}\x1b[0m`) // 亮青色加粗
  }
  
  if (lastBatchLine && terminal) {
    terminal.writeln(`\x1b[94m${lastBatchLine}\x1b[0m`) // 蓝色
  }
  
  if (lastProgressLine && terminal) {
    terminal.writeln(`\x1b[95m${lastProgressLine}\x1b[0m`) // 紫色
  }
  
  // 滚动到底部
  if (terminal) {
    terminal.scrollToBottom()
  }
}

// 复制日志
const copyLogs = () => {
  if (logs.value.length === 0) return
  
  const logText = logs.value.join('\n')
  navigator.clipboard.writeText(logText)
    .then(() => {
      $q.notify({
        type: 'positive',
        message: t('model.notifications.copyLogs'),
        position: 'top',
        timeout: 1000
      })
    })
    .catch(err => {
      console.error('Failed to copy logs:', err)
      $q.notify({
        type: 'negative',
        message: t('model.notifications.copyLogsFailed'),
        position: 'top'
      })
    })
}

// 滚动日志到底部
const scrollLogsToBottom = () => {
  if (terminal) {
    terminal.scrollToBottom()
  }
}

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', () => {
    if (fitAddon) fitAddon.fit()
  })
  
  if (terminal) {
    terminal.dispose()
    terminal = null
  }
})

// 监听日志面板展开事件
watch(() => activeMode.value, (newMode) => {
  if (newMode === 'logs' && selectedModel.value?.status === ModelStatus.TRAINING) {
    nextTick(() => {
      initTerminal()
      fetchModelLogs()
    })
  }
})

// 初始化加载
onMounted(async () => {
  // 加载数据集
  await loadDatasets()
  
  // 加载模型列表
  try {
    models.value = await modelService.getModels()
    
    // 如果有路由参数指定模型ID，自动选择该模型
    if (props.modelId) {
      const model = models.value.find(m => m.id === props.modelId)
      if (model) {
        selectModel(model)
      }
    }
    
    // 如果有路由参数指定模式，切换到该模式
    if (props.mode === 'test') {
      activeMode.value = 'test'
    }
  } catch (error) {
    console.error('Failed to load models:', error)
    $q.notify({
      type: 'negative',
      message: '加载模型列表失败',
      position: 'top',
    })
  }
})

// 文件浏览相关
const modelFiles = ref<ModelFile[]>([])
const currentPath = ref('')
const pathSegments = computed(() => currentPath.value ? currentPath.value.split('/') : [])
const previewDialog = ref(false)
const previewFile = ref<ModelFile | null>(null)
const previewUrl = ref('')
const previewContent = ref('')

// 获取模型文件列表
const fetchModelFiles = async () => {
  if (!selectedModel.value) return
  
  try {
    const response = await modelService.getModelFiles(selectedModel.value.id, currentPath.value)
    modelFiles.value = response.files
  } catch (error) {
    console.error('Failed to fetch model files:', error)
    $q.notify({
      type: 'negative',
      message: '获取模型文件列表失败',
      position: 'top'
    })
    
    // 模拟数据，以防后端API不存在
    simulateModelFiles()
  }
}

// 模拟模型文件数据（临时使用，实际应使用后端API）
const simulateModelFiles = () => {
  if (currentPath.value === '') {
    // 根目录
    modelFiles.value = [
      { name: 'weights', path: 'weights', isDir: true, size: 0, modifiedTime: new Date().toISOString() },
      { name: 'train_batch0.jpg', path: 'train_batch0.jpg', isDir: false, size: 50380, modifiedTime: new Date().toISOString() },
      { name: 'train_batch1.jpg', path: 'train_batch1.jpg', isDir: false, size: 42529, modifiedTime: new Date().toISOString() },
      { name: 'train_batch2.jpg', path: 'train_batch2.jpg', isDir: false, size: 57003, modifiedTime: new Date().toISOString() },
      { name: 'results.png', path: 'results.png', isDir: false, size: 345409, modifiedTime: new Date().toISOString() },
      { name: 'results.csv', path: 'results.csv', isDir: false, size: 29866, modifiedTime: new Date().toISOString() },
      { name: 'confusion_matrix.png', path: 'confusion_matrix.png', isDir: false, size: 86049, modifiedTime: new Date().toISOString() },
      { name: 'labels.jpg', path: 'labels.jpg', isDir: false, size: 80495, modifiedTime: new Date().toISOString() },
      { name: 'args.yaml', path: 'args.yaml', isDir: false, size: 1597, modifiedTime: new Date().toISOString() },
    ]
  } else if (currentPath.value === 'weights') {
    // weights目录
    modelFiles.value = [
      { name: 'best.pt', path: 'weights/best.pt', isDir: false, size: 6275555, modifiedTime: new Date().toISOString() },
      { name: 'last.pt', path: 'weights/last.pt', isDir: false, size: 6275555, modifiedTime: new Date().toISOString() },
    ]
  } else {
    // 其他目录
    modelFiles.value = []
  }
}

// 导航到根目录
const navigateToRoot = () => {
  currentPath.value = ''
  fetchModelFiles()
}

// 导航到特定路径
const navigateToPath = (index: number) => {
  currentPath.value = pathSegments.value.slice(0, index + 1).join('/')
  fetchModelFiles()
}

// 导航到上一级
const navigateUp = () => {
  const segments = currentPath.value.split('/')
  segments.pop()
  currentPath.value = segments.join('/')
  fetchModelFiles()
}

// 处理文件点击
const handleFileClick = (file: ModelFile) => {
  if (file.isDir) {
    currentPath.value = file.path
    fetchModelFiles()
  } else if (isPreviewable(file.name)) {
    openPreview(file)
  } else {
    downloadSelectedFile(file)
  }
}

// 打开文件预览
const openPreview = (file: ModelFile) => {
  previewFile.value = file
  loadPreview(file)
  previewDialog.value = true
}

// 加载文件预览
const loadPreview = async (file: ModelFile) => {
  if (!selectedModel.value) return
  
  if (isImageFile(file.name)) {
    // 使用modelService获取图片预览URL
    previewUrl.value = modelService.getFilePreviewUrl(selectedModel.value.id, file.path)
    previewContent.value = ''
  } else if (isTextFile(file.name)) {
    try {
      // 使用modelService获取文件内容
      const response = await modelService.getFileContent(selectedModel.value.id, file.path)
      previewContent.value = response.content
    } catch (error) {
      console.error('Failed to load file content:', error)
      
      // 使用模拟内容
      if (file.name.endsWith('.yaml')) {
        previewContent.value = `# 训练参数\ntrain: ../train/images\nval: ../valid/images\n\nncls: 3\nnames: ['person', 'car', 'bicycle']\n\nephocs: 50\nbatch: 16\nimg_size: 640`
      } else if (file.name.endsWith('.csv')) {
        previewContent.value = `epoch,train_loss,val_loss,precision,recall,mAP50,mAP50-95\n0,1.592,1.235,0.6257,0.5382,0.5932,0.4022\n1,1.023,0.876,0.7235,0.6821,0.7135,0.5124\n2,0.692,0.533,0.8353,0.7921,0.8235,0.6532`
      } else {
        previewContent.value = `无法加载文件内容：${file.name}`
      }
    }
    
    previewUrl.value = ''
  }
}

// 下载文件
const downloadSelectedFile = (file?: ModelFile) => {
  const fileToDownload = file || previewFile.value
  if (!fileToDownload || !selectedModel.value) return
  
  // 使用modelService获取下载URL
  const downloadUrl = modelService.getFileDownloadUrl(selectedModel.value.id, fileToDownload.path)
  
  // 创建一个下载链接并点击
  const a = document.createElement('a')
  a.href = downloadUrl
  a.download = fileToDownload.name
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  
  $q.notify({
    type: 'positive',
    message: t('model.notifications.downloadStarted', { name: fileToDownload.name }),
    position: 'top'
  })
}

// 检查文件是否可预览
const isPreviewable = (filename: string) => {
  return isImageFile(filename) || isTextFile(filename)
}

// 检查是否为图片文件
const isImageFile = (filename?: string) => {
  if (!filename) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
  return imageExtensions.some(ext => filename.toLowerCase().endsWith(ext))
}

// 检查是否为文本文件
const isTextFile = (filename?: string) => {
  if (!filename) return false
  const textExtensions = ['.txt', '.csv', '.yaml', '.yml', '.json', '.log', '.md']
  return textExtensions.some(ext => filename.toLowerCase().endsWith(ext))
}

// 获取文件图标
const getFileIcon = (file: ModelFile) => {
  if (file.isDir) return 'folder'
  
  const filename = file.name.toLowerCase()
  if (isImageFile(filename)) return 'image'
  if (filename.endsWith('.csv')) return 'table_chart'
  if (filename.endsWith('.pt')) return 'psychology'
  if (filename.endsWith('.yaml') || filename.endsWith('.yml')) return 'settings'
  if (filename.endsWith('.json')) return 'data_object'
  
  return 'insert_drive_file'
}

// 获取文件图标颜色
const getFileColor = (file: ModelFile) => {
  if (file.isDir) return 'amber'
  
  const filename = file.name.toLowerCase()
  if (isImageFile(filename)) return 'green'
  if (filename.endsWith('.csv')) return 'blue'
  if (filename.endsWith('.pt')) return 'purple'
  if (filename.endsWith('.yaml') || filename.endsWith('.yml')) return 'deep-orange'
  
  return 'grey'
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${units[i]}`
}

// 格式化修改时间
const formatModifiedTime = (timeStr: string) => {
  const date = new Date(timeStr)
  return date.toLocaleString()
}

// 当选择模型或切换到文件模式时加载文件
watch([() => selectedModel.value, () => activeMode.value], ([newModel, newMode]) => {
  if (newModel && newMode === 'files') {
    navigateToRoot()
  }
})

// 添加复制模型ID的方法
const copyModelId = (id: number, event: Event) => {
  event.stopPropagation()
  const model = models.value.find(m => m.id === id)
  if (model) {
    const idText = `${model.id}`
    navigator.clipboard.writeText(idText)
      .then(() => {
        $q.notify({
          type: 'positive',
          message: t('model.notifications.copyModelId'),
          position: 'top',
          timeout: 1000
        })
      })
      .catch(err => {
        console.error('Failed to copy model ID:', err)
        $q.notify({
          type: 'negative',
          message: t('model.notifications.copyModelIdFailed'),
          position: 'top'
        })
      })
  }
}
</script>

<style lang="scss" scoped>
.model-page {
  background: var(--dark-page);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.model-card {
  background: var(--dark-card);
  flex: 1 1 300px;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: auto;
}

.training-card,
.progress-card,
.mode-switch-card {
  background: var(--dark-card);
  flex: 1 1 500px;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: auto;
}

.mode-switch-card {
  min-height: auto;
}

.q-card-section {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 添加更多样式 */
.progress-container {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  padding: 16px;
}

.progress-label {
  font-weight: 500;
  width: 60px;
  text-align: center;
}

.progress-value {
  font-weight: 500;
  width: 60px;
  text-align: center;
}

.progress-bar {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.metric-card {
  background-color: rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
}

/* 日志相关样式 */
.log-line {
  margin-bottom: 2px;
  padding: 1px 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-stdout {
  color: #e6e6e6;
}

.log-stderr {
  color: #f97583;
}

.log-error {
  color: #ff6b6b;
}

.log-warning {
  color: #ffd166;
}

.log-info {
  color: #76e4ff;
}

.log-system {
  color: #50fa7b;
}

.log-progress {
  color: #64d8fb;
  background-color: rgba(0, 0, 0, 0.2);
  padding: 2px 6px;
  margin: 2px 0;
  border-radius: 3px;
  border-left: 3px solid #64d8fb;
}

.log-epoch-progress {
  color: #5eead4;
  background-color: rgba(0, 0, 0, 0.3);
  font-weight: bold;
  border-left: 3px solid #5eead4;
}

.log-batch-progress {
  color: #a5b4fc;
  background-color: rgba(0, 0, 0, 0.25);
  border-left: 3px solid #a5b4fc;
}

/* 终端容器样式 */
.terminal-container {
  font-family: Menlo, Monaco, "Courier New", monospace;
  background-color: #1e1e1e;
  padding: 0;
  margin: 0;
  box-shadow: 0 3px 5px rgba(0, 0, 0, 0.2);
}

.files-card {
  background: var(--dark-card);
  flex: 1 1 500px;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: auto;
}

.file-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
  max-height: 80vh;
  overflow: auto;
}

.text-preview {
  width: 100%;
  padding: 16px;
  background-color: #1e1e1e;
  border-radius: 4px;
  overflow: auto;
}

.text-content {
  font-family: 'Courier New', Courier, monospace;
  white-space: pre-wrap;
  word-break: break-word;
  color: #e6e6e6;
  margin: 0;
  line-height: 1.5;
}

.image-preview {
  text-align: center;
}

.unknown-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9e9e9e;
}

/* 模型列表选中样式 */
.model-card {
  background: var(--dark-card);
  
  .q-list {
    border-radius: 8px;
    background: var(--dark-page);
    padding: 4px;
    
    .q-item {
      border-radius: 6px;
      margin: 2px 0;
      min-height: 56px;
      transition: all 0.3s ease;
      
      &:hover {
        background: var(--industrial-blue-50);
      }
      
      &.model-selected {
        background: var(--industrial-blue-50);
        border-left: 3px solid var(--primary);
      }
    }
  }
}

/* 添加工业风格变量 */
:root {
  --industrial-blue-50: rgba(25, 118, 210, 0.1);
  --dark-card: #1e1e1e;
  --dark-page: #121212;
  --primary: #1976d2;
  --dark-separator: rgba(255, 255, 255, 0.07);
}

/* 模型ID徽标样式 */
.model-id-badge {
  vertical-align: super;
  font-size: 0.75em;
  margin-left: 5px;
  transition: all 0.2s ease;
}

.model-id-badge:hover {
  transform: scale(1.1);
  opacity: 0.9;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>