<template>
  <q-page class="realtime-page q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- 相机预览区域 -->
      <div class="col-12 col-lg-8">
        <q-card class="camera-card">
          <q-card-section>
            <div class="row items-center">
              <div class="text-h6">{{ t('realtime.title') }}</div>
              <q-space />
              <q-select
                v-model="selectedCamera"
                :options="cameras"
                option-label="name"
                option-value="id"
                color="primary"
                :label="t('realtime.camera.select')"
                dense
                outlined
                class="camera-select"
                style="min-width: 180px"
                :disable="processingStream || isProcessingImage"
              >
                <template v-slot:option="{ itemProps, opt, selected }">
                  <q-item v-bind="itemProps">
                    <q-item-section>
                      <q-item-label>{{ opt.name }}</q-item-label>
                    </q-item-section>
                    <q-item-section avatar>
                      <q-badge :color="opt.status === 'online' ? 'positive' : 'negative'">
                        {{ deviceStatusText(opt.status) }}
                      </q-badge>
                    </q-item-section>
                  </q-item>
                </template>
                
                <template v-slot:selected>
                  <div v-if="selectedCamera">
                    {{ selectedCamera.name }}
                    <q-badge class="q-ml-sm" :color="selectedCamera.status === 'online' ? 'positive' : 'negative'">
                      {{ deviceStatusText(selectedCamera.status) }}
                    </q-badge>
                  </div>
                </template>
              </q-select>
            </div>
            
            <div class="row q-col-gutter-md q-mt-md">
              <!-- 视频预览 -->
              <div :class="processingStream ? 'col-6' : 'col-12'">
                <div class="view-label q-mb-sm">{{ t('realtime.camera.video') }}</div>
                <camera-capture 
                  class="source-preview"
                  :stream-url="selectedCamera ? getStreamUrl(selectedCamera) : ''"
                  @capture="onCapture"
                  @error="onCameraError"
                  @status-change="updateCameraStatus"
                  @stream-ready="handleStreamReady"
                  @stream-error="handleStreamError"
                  :detection-result="detectionResult"
                  :is-processing="isProcessingImage" />
              </div>
              
              <!-- 处理后的视频流显示 -->
              <div v-if="processingStream" class="col-6">
                <div class="view-label q-mb-sm">{{ t('realtime.camera.processed') }}</div>
                <div class="processed-stream-container">
                  <img 
                    v-if="processedStreamUrl" 
                    :src="processedStreamUrl" 
                    class="processed-stream" 
                    alt="处理后视频流"
                    @error="handleProcessedStreamError"
                    @load="handleProcessedStreamLoaded"
                  />
                  <div v-else class="no-stream-placeholder">
                    <q-spinner color="primary" size="48px" />
                    <div class="text-grey-7 q-mt-sm">{{ t('realtime.camera.processing') }}</div>
                  </div>
                </div>
                <div class="stream-info q-mt-sm text-center">
                  <q-badge v-if="processedStreamUrl" color="positive">{{ t('realtime.camera.streamActive') }}</q-badge>
                  <q-badge v-else color="warning">{{ t('realtime.camera.streamWaiting') }}</q-badge>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 检测结果区域 -->
      <div class="col-12 col-lg-4">
        <!-- 操作选择面板 -->
        <q-card class="operation-card">
          <q-card-section>
            <div class="text-h6">{{ t('realtime.operation.title') }}</div>
            <div class="q-mt-md">
              <q-select
                v-model="selectedOperation"
                :options="mergedOperationOptions"
                :label="t('realtime.operation.select')"
                outlined
                dense
                emit-value
                map-options
                option-label="label"
                option-value="value"
                option-disable="disable"
                :loading="operationsLoading"
                :rules="[(val: string) => !!val && val !== 'none' || t('realtime.operation.selectRequired')]"
              >
                <template v-slot:option="{ itemProps, opt, selected, toggleOption }">
                  <q-item v-bind="itemProps" @click="toggleOption(opt)">
                    <q-item-section>
                      <q-item-label :class="{'text-weight-bold': opt.header}">{{ opt.label }}</q-item-label>
                    </q-item-section>
                    
                    <q-item-section v-if="opt.description" side>
                      <q-tooltip>{{ opt.description }}</q-tooltip>
                      <q-icon name="info" color="grey-6" size="xs" />
                    </q-item-section>
                    
                    <q-item-section v-if="opt.type && !opt.disable" side>
                      <q-badge :color="opt.type === 'operation' ? 'primary' : 'purple'">
                        {{ t(`realtime.operation.types.${opt.type === 'operation' ? 'single' : 'pipeline'}`) }}
                      </q-badge>
                    </q-item-section>
                    
                    <q-item-section v-if="opt.supportsDetection" side>
                      <q-badge color="green">{{ t('realtime.operation.detection') }}</q-badge>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
              
              <div class="row q-col-gutter-sm q-mt-md">
                <div class="col">
                  <q-btn 
                    color="primary" 
                    :disable="!detectionResult || !selectedOperation || selectedOperation === 'none'" 
                    :label="t('realtime.operation.apply')"
                    icon="auto_fix_high"
                    @click="captureOnce" 
                    class="full-width"
                  />
                </div>
                <div class="col">
                  <q-btn
                    :color="processingStream ? 'grey' : 'secondary'"
                    :icon="processingStream ? 'stop' : 'play_arrow'"
                    :label="processingStream ? t('realtime.operation.stopStream') : t('realtime.operation.startStream')"
                    @click="toggleStreamProcessing"
                    :disable="!selectedCamera || selectedCamera.status !== 'online' || !selectedOperation || selectedOperation === 'none'"
                    class="full-width"
                  />
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- 处理结果预览 -->
        <q-card v-if="processedResult" class="processed-card q-mt-md">
          <q-card-section>
            <div class="text-h6">{{ t('realtime.result.title') }}</div>
            <div class="q-mt-md">
              <div class="processed-image-container">
                <img :src="processedResult.imageData" class="processed-image" />
              </div>
              <div class="text-center q-mt-sm">
                <q-badge color="secondary">{{ getOperationName(selectedOperation) }}</q-badge>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <q-card class="result-card q-mt-md">
          <q-card-section>
            <div class="text-h6">{{ t('realtime.result.title') }}</div>
            <div v-if="detectionResult" class="result-container q-mt-md">
              <div :class="`text-h5 text-center ${detectionResult.passed ? 'text-positive' : 'text-negative'}`">
                {{ t(`realtime.result.status.${detectionResult.passed ? 'pass' : 'fail'}`) }}
              </div>
              <q-list separator>
                <q-item>
                  <q-item-section>
                    <q-item-label>{{ t('realtime.result.details.time') }}</q-item-label>
                    <q-item-label caption>{{ formatDateTime(detectionResult.timestamp) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="detectionResult.sourceType">
                  <q-item-section>
                    <q-item-label>{{ t('realtime.result.details.source') }}</q-item-label>
                    <q-item-label caption>{{ detectionResult.sourceType }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label>{{ t('realtime.result.details.text') }}</q-item-label>
                    <q-item-label caption>{{ detectionResult.text || t('realtime.result.details.noText') }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label>{{ t('realtime.result.details.confidence') }}</q-item-label>
                    <q-item-label caption>{{ detectionResult.confidence ? detectionResult.confidence.toFixed(1) + '%' : 'N/A' }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="detectionResult.errorReason">
                  <q-item-section>
                    <q-item-label>{{ t('realtime.result.details.error') }}</q-item-label>
                    <q-item-label caption class="text-negative">{{ detectionResult.errorReason }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="detectionResult.fileName">
                  <q-item-section>
                    <q-item-label>{{ t('realtime.result.details.filename') }}</q-item-label>
                    <q-item-label caption>{{ detectionResult.fileName }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
            <div v-else class="no-result-placeholder q-mt-md">
              <q-icon name="pending" size="64px" color="grey-7" class="q-mb-md" />
              <div class="text-grey-7">{{ t('realtime.result.waiting') }}</div>
            </div>
          </q-card-section>
        </q-card>

        <!-- 批量处理结果展示 -->
        <q-card v-if="batchResults.length > 0" class="batch-results-card q-mt-md">
          <q-card-section>
            <div class="row items-center">
              <div class="text-h6">批量识别结果</div>
              <q-space />
              <q-badge color="primary" class="q-mr-sm">共 {{ batchResults.length }} 张图片</q-badge>
              <q-badge :color="batchProcessing ? 'secondary' : 'positive'">
                {{ batchProcessing ? '处理中' : '处理完成' }}
              </q-badge>
            </div>
            
            <q-carousel
              v-model="activeResultSlide"
              transition-prev="slide-right"
              transition-next="slide-left"
              swipeable
              animated
              arrows
              navigation
              padding
              height="400px"
              class="bg-dark shadow-1 rounded-borders q-mt-md"
            >
              <q-carousel-slide v-for="(result, index) in batchResults" :key="index" :name="index" class="column no-wrap bg-dark">
                <div class="row fit justify-center">
                  <div class="col-12 col-md-6 q-pa-xs">
                    <div class="text-h6 text-center text-white">原始图像</div>
                    <div class="batch-image-container">
                      <img :src="result.originalImage" class="batch-image" />
                    </div>
                  </div>
                  <div class="col-12 col-md-6 q-pa-xs">
                    <div class="text-h6 text-center text-white">处理结果</div>
                    <div class="batch-image-container" v-if="!result.error">
                      <img :src="result.processedImage" class="batch-image" />
                    </div>
                    <div class="batch-error-container" v-else>
                      <q-icon name="error" size="64px" color="negative" />
                      <div class="text-negative q-mt-md">处理失败: {{ result.error }}</div>
                    </div>
                  </div>
                  <div class="col-12 q-mt-md">
                    <q-list bordered separator class="bg-dark text-white">
                      <q-item>
                        <q-item-section>
                          <q-item-label caption class="text-grey-5">文件名</q-item-label>
                          <q-item-label>{{ result.fileName }}</q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item>
                        <q-item-section>
                          <q-item-label caption class="text-grey-5">识别状态</q-item-label>
                          <q-item-label>
                            <q-badge :color="result.passed ? 'positive' : 'negative'">
                              {{ result.passed ? '通过' : '失败' }}
                            </q-badge>
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item>
                        <q-item-section>
                          <q-item-label caption class="text-grey-5">识别文本</q-item-label>
                          <q-item-label>{{ result.text || '未识别到文本' }}</q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item>
                        <q-item-section>
                          <q-item-label caption class="text-grey-5">置信度</q-item-label>
                          <q-item-label>{{ result.confidence ? result.confidence.toFixed(1) + '%' : 'N/A' }}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </div>
                </div>
                <div class="absolute-bottom text-center q-mb-sm">
                  <q-badge outline color="primary">{{ index + 1 }} / {{ batchResults.length }}</q-badge>
                </div>
              </q-carousel-slide>
            </q-carousel>
            
            <!-- 批量结果统计 -->
            <div class="batch-summary q-mt-lg">
              <div class="row q-col-gutter-md">
                <div class="col-12 col-md-4">
                  <q-card flat bordered class="text-center bg-dark text-white">
                    <q-card-section>
                      <div class="text-h6">总计</div>
                      <div class="text-h4">{{ batchResults.length }}</div>
                      <div class="text-caption text-grey-5">图片数量</div>
                    </q-card-section>
                  </q-card>
                </div>
                
                <div class="col-12 col-md-4">
                  <q-card flat bordered class="text-center bg-dark text-white">
                    <q-card-section>
                      <div class="text-h6">通过</div>
                      <div class="text-h4 text-positive">{{ batchResults.filter(r => r.passed).length }}</div>
                      <div class="text-caption text-grey-5">识别成功</div>
                    </q-card-section>
                  </q-card>
                </div>
                
                <div class="col-12 col-md-4">
                  <q-card flat bordered class="text-center bg-dark text-white">
                    <q-card-section>
                      <div class="text-h6">失败</div>
                      <div class="text-h4 text-negative">{{ batchResults.filter(r => !r.passed).length }}</div>
                      <div class="text-caption text-grey-5">识别失败</div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- 相机控制面板 -->
        <q-card class="control-card q-mt-md">
          <q-card-section>
            <div class="text-h6">{{ t('realtime.control.title') }}</div>
            <div class="q-mt-md">
              <q-btn-group spread>
                <q-btn 
                  :color="autoDetect ? 'grey' : 'primary'" 
                  :icon="autoDetect ? 'not_interested' : 'play_arrow'" 
                  :label="autoDetect ? t('realtime.control.autoDetect.stop') : t('realtime.control.autoDetect.start')"
                  @click="toggleAutoDetect"
                  :disable="(!selectedCamera || selectedCamera.status !== 'online') && !uploadedImage" />
                <q-btn 
                  color="secondary" 
                  icon="photo_camera" 
                  :label="t('realtime.control.capture')" 
                  @click="captureOnce"
                  :disable="!isStreaming && !uploadedImage" />
              </q-btn-group>
              
              <q-list class="q-mt-md">
                <q-item>
                  <q-item-section>
                    <q-item-label>{{ t('realtime.control.exposure') }}</q-item-label>
                    <q-slider v-model="cameraSettings.exposure" :min="0" :max="100" label 
                              @update:model-value="(val: number) => updateSettings('exposure', val || 0)"
                              :disable="!selectedCamera || selectedCamera.status !== 'online'" />
                  </q-item-section>
                  <q-item-section avatar>
                    <q-badge color="primary">{{ cameraSettings.exposure }}</q-badge>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label>{{ t('realtime.control.gain') }}</q-item-label>
                    <q-slider v-model="cameraSettings.gain" :min="0" :max="100" label 
                              @update:model-value="(val: number) => updateSettings('gain', val || 0)"
                              :disable="!selectedCamera || selectedCamera.status !== 'online'" />
                  </q-item-section>
                  <q-item-section avatar>
                    <q-badge color="primary">{{ cameraSettings.gain }}</q-badge>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'
import CameraCapture from '../components/capture/CameraCapture.vue'
import { cameraService } from '@/services/camera'
import { settingsService, Device } from '@/services/settings'
import { CVOperation, CVOperationService, ParamType } from '@/services/cv_operation'
import { Pipeline, PipelineService } from '@/services/pipeline'
import { detectionService } from '@/services/detection'
import { apiService } from '@/services/api'
import axios from 'axios'

// 修复前端代码中的类型错误
declare global {
  interface ImportMeta {
    readonly env: Record<string, string>;
  }
}

// 添加API基础URL变量
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// 扩展操作和流水线接口，添加hasDetectionOutput属性
declare module '@/services/cv_operation' {
  interface CVOperation {
    hasDetectionOutput?: boolean;
  }
}

declare module '@/services/pipeline' {
  interface Pipeline {
    hasDetectionOutput?: boolean;
  }
}

const $q = useQuasar()
const { t } = useI18n()

// 确认cameraService实例已正确导入
console.log('cameraService实例:', cameraService)

const cvOperationService = new CVOperationService()
const pipelineService = new PipelineService()

// 相机列表和选中的相机
const cameras = ref<Device[]>([])
const selectedCamera = ref<Device | null>(null)
const autoDetect = ref(false)
const isStreaming = ref(false)
let autoDetectInterval: number | null = null

// 相机设置
const cameraSettings = reactive({
  exposure: 50,
  gain: 50,
  autoFocus: true
})

// 检测结果
const detectionResult = ref<any>(null)

// 实时处理状态
const processingStream = ref(false)
// 处理后的视频流URL
const processedStreamUrl = ref<string | null>(null)

// 操作选择和处理结果
const selectedOperation = ref<string | null>(null)
const processedResult = ref<any>(null)

// 操作列表
const cvOperations = ref<CVOperation[]>([])
const pipelines = ref<Pipeline[]>([])
const operationsLoading = ref(false)

// 添加一个标记表示是否有上传的图片
const uploadedImage = ref(false);

// 添加缺少的状态变量
const cameraConnected = ref(false)
const cameraError = ref(false)

// 添加新的状态变量
const isProcessingImage = ref(false)
const streamReady = ref(false)
const retryCount = ref(0)
const MAX_RETRIES = 5
const RETRY_DELAY = 2000

// 添加批量处理状态和结果
const batchResults = ref<any[]>([])
const batchProcessing = ref(false)
const batchProgress = ref(0)
const totalBatchImages = ref(0)
const activeResultSlide = ref(0)

// 修改合并操作选项接口，增加类型定义
interface OperationOption {
  label: string;
  value: string;
  type: string | null;
  header?: boolean;
  disable?: boolean;
  description?: string | undefined;
  operation?: any;
  supportsDetection?: boolean;
}

// 加载操作列表
const loadOperations = async () => {
  try {
    operationsLoading.value = true
    
    // 并行加载操作和流水线
    const [operations, pipes] = await Promise.all([
      cvOperationService.getOperations(),
      pipelineService.getPipelines()
    ])
    
    // 过滤出具有图像输入、图像输出和检测结果输出的操作
    cvOperations.value = operations.filter(op => {
      // 检查输入参数是否包含图片类型
      const hasImageInput = op.inputParams.some(param =>
        param.type === ParamType.IMAGE || param.name.toLowerCase().includes('image')
      )

      // 检查输出参数是否包含图片类型
      const hasImageOutput = op.outputParams.some(param =>
        param.type === ParamType.IMAGE || param.name.toLowerCase().includes('image')
      )
      
      // 检查是否有检测结果输出
      const hasDetectionOutput = op.outputParams.some(param => {
        // 检查参数名称是否包含"result"、"detect"或"text"关键字
        const nameHints = param.name.toLowerCase().includes('result') || 
                          param.name.toLowerCase().includes('detect') || 
                          param.name.toLowerCase().includes('text');
                          
        // 检查参数描述是否包含这些关键字
        const descHints = param.description && (
                          param.description.toLowerCase().includes('检测') ||
                          param.description.toLowerCase().includes('识别') ||
                          param.description.toLowerCase().includes('detection') ||
                          param.description.toLowerCase().includes('recognition'));
                          
        return nameHints || descHints || param.type === ParamType.OBJECT;
      });

      // 只需要满足图像输入和输出的条件，检测输出是可选的
      // 添加一个属性标记哪些操作提供检测输出，以便后续处理
      op.hasDetectionOutput = hasDetectionOutput;
      return hasImageInput && hasImageOutput;
    })
    
    // 对于流水线，同样只要求有图像输入和输出
    pipelines.value = pipes.filter(pipe => {
      // 检查输入参数是否包含图片类型
      const hasImageInput = pipe.inputParams.some((param: any) =>
        param.type === ParamType.IMAGE || param.name.toLowerCase().includes('image')
      );

      // 检查输出参数是否包含图片类型
      const hasImageOutput = pipe.outputParams.some((param: any) =>
        param.type === ParamType.IMAGE || param.name.toLowerCase().includes('image')
      );

      // 检查是否有检测结果输出
      const hasDetectionOutput = pipe.outputParams.some((param: any) => {
        const nameHints = param.name.toLowerCase().includes('result') || 
                          param.name.toLowerCase().includes('detect') || 
                          param.name.toLowerCase().includes('text');
                          
        const descHints = param.description && (
                          param.description.toLowerCase().includes('检测') ||
                          param.description.toLowerCase().includes('识别') ||
                          param.description.toLowerCase().includes('detection') ||
                          param.description.toLowerCase().includes('recognition'));
                          
        return nameHints || descHints || param.type === ParamType.OBJECT;
      });

      // 添加属性标记是否提供检测输出
      pipe.hasDetectionOutput = hasDetectionOutput;
      return hasImageInput && hasImageOutput;
    });
    
    // 如果过滤后没有可用操作，记录警告
    if (cvOperations.value.length === 0 && pipelines.value.length === 0) {
      console.warn('没有找到包含图像输入和图像输出的操作');
      $q.notify({
        type: 'warning',
        message: '没有找到合适的图像处理操作，请确保操作有图像输入和输出',
        position: 'top',
        timeout: 5000
      });
    }
    
  } catch (error) {
    console.error('加载操作列表失败:', error)
    $q.notify({
      type: 'negative',
      message: '加载操作列表失败',
      position: 'top'
    })
  } finally {
    operationsLoading.value = false
  }
}

// 合并操作选项
const mergedOperationOptions = computed<OperationOption[]>(() => {
  const options: OperationOption[] = [
    { label: '无操作', value: 'none', type: null }
  ]
  
  // 添加单步处理分组标题
  if (cvOperations.value.length > 0) {
    options.push({ label: '单步处理', value: 'header1', type: null, header: true, disable: true })
    
    // 添加单步处理操作
    cvOperations.value.forEach(op => {
      options.push({
        label: op.name,
        value: `operation:${op.id}`,
        description: op.description || undefined,
        type: 'operation',
        operation: op,
        supportsDetection: op.hasDetectionOutput === true
      })
    })
  }
  
  // 添加流水线处理分组标题
  if (pipelines.value.length > 0) {
    options.push({ label: '流水线处理', value: 'header2', type: null, header: true, disable: true })
    
    // 添加流水线处理操作
    pipelines.value.forEach(pipeline => {
      options.push({
        label: pipeline.name,
        value: `pipeline:${pipeline.id}`,
        description: pipeline.description || undefined,
        type: 'pipeline',
        operation: pipeline,
        supportsDetection: pipeline.hasDetectionOutput === true
      })
    })
  }
  
  return options
})

// 获取相机列表
const loadCameras = async () => {
  try {
    cameras.value = await settingsService.getDevices('camera')
    
    // 检查相机配置是否完整
    cameras.value.forEach(camera => {
      if (!camera.config) {
        camera.config = {};
      }
      // 确保有正确的默认值
      if (!camera.config.source) {
        camera.config.source = `device:${camera.id}`;
      }
    });
    
    // 如果有在线相机，默认选择第一个在线相机
    const onlineCamera = cameras.value.find(c => c.status === 'online')
    if (onlineCamera && !selectedCamera.value) {
      selectCamera(onlineCamera)
    } else if (cameras.value.length > 0 && !selectedCamera.value) {
      // 如果没有在线相机但有相机，选择第一个
      selectCamera(cameras.value[0])
    }
  } catch (error) {
    console.error('获取相机列表失败:', error)
    $q.notify({
      type: 'negative',
      message: '获取相机列表失败',
      position: 'top'
    })
  }
}

// 选择相机
const selectCamera = (camera: Device) => {
  console.log('选择相机:', camera)
  // 确保相机有配置
  if (!camera.config) {
    camera.config = {}
  }
  selectedCamera.value = camera
}

// 更新相机设置
const updateSettings = async (key: string, value: number) => {
  if (!selectedCamera.value) return
  
  try {
    // 创建新的配置对象
    const newConfig = { ...selectedCamera.value.config, [key]: value }
    
    // 使用settingsService更新设备
    await settingsService.updateDevice(selectedCamera.value.id, {
      config: newConfig
    })
    
    // 更新本地状态
    if (selectedCamera.value) {
      selectedCamera.value.config[key] = value
    }
  } catch (error) {
    console.error('更新相机设置失败:', error)
    $q.notify({
      type: 'negative',
      message: '更新相机设置失败',
      position: 'top'
    })
  }
}

// 获取流URL - 使用正确的摄像头ID逻辑
const getStreamUrl = (camera: Device | null): string => {
  if (!camera) {
    console.log('getStreamUrl: 没有提供摄像头')
    return ''
  }
  
  // 如果配置中已经有stream_url，直接使用
  if (camera.config?.stream_url) {
    console.log('getStreamUrl: 使用配置的stream_url', camera.config.stream_url)
    return camera.config.stream_url
  }
  
  // 提取摄像头设备ID
  let cameraId: string
  
  if (camera.config?.source && camera.config.source.startsWith('device:')) {
    // 从source字段提取设备ID
    const devicePart = camera.config.source.split(':')[1]
    cameraId = devicePart || '0' // 默认使用设备0
  } else if (camera.config?.device_id !== undefined) {
    // 使用明确设置的device_id
    cameraId = camera.config.device_id.toString()
  } else {
    // 回退到设备0
    cameraId = '0'
  }
  
  // 构建API流地址
  const streamUrl = cameraService.getCameraStreamUrl(`camera_${cameraId}`)
  console.log('getStreamUrl: API流地址', streamUrl)
  return streamUrl
}

// 修改处理相机状态变更的函数
const updateCameraStatus = (status: string) => {
  console.log('相机状态变更:', status)
  
  // 根据状态更新界面和功能
  switch (status) {
    case 'online':
      cameraConnected.value = true
      cameraError.value = false
      isStreaming.value = true
      streamReady.value = true
      retryCount.value = 0
      break
      
    case 'offline':
    case 'error':
      cameraConnected.value = false
      cameraError.value = true
      isStreaming.value = false
      streamReady.value = false
      
      // 如果正在处理流，需要停止
      if (processingStream.value) {
        stopStreamProcessing()
      }
      break
      
    case 'connecting':
      cameraConnected.value = false
      cameraError.value = false
      isStreaming.value = true
      streamReady.value = false
      break
      
    case 'processing':
      cameraConnected.value = true
      cameraError.value = false
      isStreaming.value = true
      break
      
    case 'stopped':
      isStreaming.value = false
      break
      
    case 'uploaded':
      // 当图片上传时，我们不是在流式传输，但图片已经上传
      isStreaming.value = false
      cameraConnected.value = false
      cameraError.value = false
      uploadedImage.value = true
      
      // 如果之前正在处理流，需要停止处理
      if (processingStream.value) {
        stopStreamProcessing()
      }
      break
  }
  
  // 通知其他组件状态变化
  emit('camera-status-change', status)
}

// 修改单次采集函数，支持无相机情况
const captureOnce = async () => {
  try {
    // 处理图像
    await processImage()
    
    $q.notify({
      type: 'positive',
      message: t('realtime.notifications.processingComplete'),
      position: 'top'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: t('realtime.notifications.processingFailed', { error: (error as Error).message }),
      position: 'top'
    })
  }
}

// 修改toggleStreamProcessing函数
const toggleStreamProcessing = async () => {
  if (processingStream.value) {
    await stopStreamProcessing()
    return
  }
  
  // 验证相机和操作选择
  if (!selectedCamera.value) {
    $q.notify({
      type: 'warning',
      message: t('realtime.notifications.selectCamera'),
      position: 'top'
    })
    return
  }
  
  if (!selectedOperation.value || selectedOperation.value === 'none') {
    $q.notify({
      type: 'warning',
      message: t('realtime.notifications.selectOperation'),
      position: 'top'
    })
    return
  }
  
  if (selectedCamera.value.status !== 'online') {
    $q.notify({
      type: 'warning',
      message: t('realtime.notifications.cameraUnavailable'),
      position: 'top'
    })
    return
  }
  
  $q.notify({
    type: 'info',
    message: t('realtime.notifications.startProcessing'),
    position: 'top'
  })
  
  try {
    const operation = selectedOperation.value
    if (!operation) {
      throw new Error(t('realtime.notifications.invalidOperation'))
    }
    
    // 启动处理流
    await startStream()
    
    $q.notify({
      type: 'positive',
      message: t('realtime.notifications.streamStarted'),
      position: 'top'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: t('realtime.notifications.streamStartFailed', { error: (error as Error).message }),
      position: 'top'
    })
  }
}

// 修改停止处理流的函数
const stopStreamProcessing = async () => {
  if (!processingStream.value) return
  
  try {
    $q.loading.show({
      message: '正在停止视频处理...',
      spinnerColor: 'primary',
      backgroundColor: 'dark',
    })
    
    // 先更新UI状态，避免继续重试
    processingStream.value = false
    processedStreamUrl.value = null
    processedStreamRetryCount = 0
    processedStreamFirstLoaded = false
    
    // 如果有选定的相机，调用API停止处理
    if (selectedCamera.value) {
      const cameraId = getCameraDeviceId(selectedCamera.value)
      console.log('停止处理摄像头ID:', cameraId)
      
      try {
        await axios.post(
          `${API_BASE_URL}/cameras/camera_${cameraId}/stop-stream`,
          null,
          { headers: { 'Content-Type': 'application/json' } }
        )
        
        console.log('已停止视频处理')
        $q.notify({ type: 'info', message: '实时处理已停止', position: 'top' })
      } catch (error: any) {
        console.error('停止处理API调用失败:', error)
        $q.notify({
          type: 'warning',
          message: '停止处理时遇到问题，请检查后端服务状态',
          position: 'top'
        })
      }
    }
  } catch (error: any) {
    console.error('停止处理流失败:', error)
    $q.notify({
      type: 'negative',
      message: `停止处理流失败: ${error.message || '未知错误'}`,
      position: 'top'
    })
  } finally {
    // 确保状态被重置
    processingStream.value = false
    processedStreamUrl.value = null
    $q.loading.hide()
  }
}

// 修改处理流错误处理和重试逻辑
const handleProcessedStreamError = () => {
  console.error('处理流加载失败，当前重试次数:', processedStreamRetryCount)
  
  if (!processingStream.value) {
    console.log('处理已停止，不再重试')
    return
  }

  // 增加重试次数上限
  const MAX_RETRIES = 5
  
  if (!processedStreamRetryCount) {
    processedStreamRetryCount = 1
    $q.notify({
      type: 'warning',
      message: '处理流加载中，正在重试...',
      position: 'top'
    })
  } else if (processedStreamRetryCount >= MAX_RETRIES) {
    console.error('处理流重试次数过多，停止处理')
    $q.notify({
      type: 'negative',
      message: '处理流加载失败，请检查相机和网络连接',
      position: 'top'
    })
    
    // 自动停止处理
    stopStreamProcessing()
    return
  }
  
  // 指数退避重试
  const retryDelay = Math.min(1000 * Math.pow(2, processedStreamRetryCount - 1), 10000)
  console.log(`将在 ${retryDelay}ms 后进行第 ${processedStreamRetryCount + 1} 次重试`)
  
  setTimeout(() => {
    if (!processingStream.value) {
      console.log('处理已停止，取消重试')
      return
    }
    
    processedStreamRetryCount++
    
    // 重新构建处理流URL
    if (selectedCamera.value && selectedOperation.value) {
      try {
        const camera = selectedCamera.value
        let cameraId = getCameraDeviceId(camera)
        
        // 解析操作信息
        const operationType = selectedOperation.value.startsWith('operation:') ? 'operation' : 'pipeline'
        const operationId = parseInt(selectedOperation.value.split(':')[1])
        
        if (isNaN(operationId)) {
          throw new Error('无效的操作ID')
        }
        
        // 构建新的URL
        const newStreamUrl = cameraService.getCameraStreamUrl(
          cameraId,
          {
            operation_id: operationId,
            operation_type: operationType
          }
        ) + `&_t=${new Date().getTime()}`
        
        console.log(`重试处理流URL (${processedStreamRetryCount}/${MAX_RETRIES}):`, newStreamUrl)
        
        // 更新图像源
        const img = document.querySelector('.processed-stream') as HTMLImageElement
        if (img) {
          img.src = newStreamUrl
        }
        
        processedStreamUrl.value = newStreamUrl
      } catch (error) {
        console.error('重建处理流URL失败:', error)
        stopStreamProcessing()
      }
    }
  }, retryDelay)
}

// 添加获取相机设备ID的辅助函数
const getCameraDeviceId = (camera: Device): string => {
  if (camera.config?.source && camera.config.source.startsWith('device:')) {
    const devicePart = camera.config.source.split(':')[1]
    return devicePart || '0'
  }
  
  if (camera.config?.device_id !== undefined) {
    return camera.config.device_id.toString()
  }
  
  return '0'
}

// 修改处理流加载成功的处理
const handleProcessedStreamLoaded = () => {
  console.log('处理流加载成功')
  // 重置重试计数
  processedStreamRetryCount = 0
  
  // 如果这是第一次加载，显示通知
  if (!processedStreamFirstLoaded) {
    processedStreamFirstLoaded = true
    $q.notify({
      type: 'positive',
      message: '处理流已连接',
      position: 'top',
      timeout: 2000
    })
  }
}

// 添加重试计数和加载状态变量
let processedStreamRetryCount = 0
let processedStreamFirstLoaded = false

// 修改切换自动检测函数，考虑上传的图片情况
const toggleAutoDetect = async () => {
  autoDetect.value = !autoDetect.value
  
  if (autoDetect.value) {
    $q.notify({
      type: 'info',
      message: t('realtime.notifications.autoDetectStarted'),
      position: 'top'
    })
  } else {
    $q.notify({
      type: 'info',
      message: t('realtime.notifications.autoDetectStopped'),
      position: 'top'
    })
  }
}

// 格式化日期时间
const formatDateTime = (date: any) => {
  if (!date) return 'N/A'
  
  const d = new Date(date)
  const pad = (n: number) => n < 10 ? `0${n}` : n
  
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

// 设备状态文本
const deviceStatusText = (status: string): string => {
  switch (status) {
    case 'online': return t('realtime.status.online')
    case 'offline': return t('realtime.status.offline')
    case 'error': return t('realtime.status.error')
    default: return t('realtime.status.unknown')
  }
}

// 监听相机选择变化
watch(selectedCamera, (newCamera) => {
  if (newCamera) {
    // 如果选择了新相机，更新控制参数
    if (newCamera.config) {
      cameraSettings.exposure = newCamera.config.exposure || 50
      cameraSettings.gain = newCamera.config.gain || 50
      cameraSettings.autoFocus = newCamera.config.autoFocus !== false
    }
    
    // 通知用户
    $q.notify({
      type: 'info',
      message: t('realtime.notifications.cameraSelected', { name: newCamera.name }),
      position: 'top'
    })
  }
})

// 组件挂载时
onMounted(async () => {
  // 先加载操作列表，因为操作是必需的
  await loadOperations()
  
  // 提示用户选择操作
  if (cvOperations.value.length > 0 || pipelines.value.length > 0) {
    $q.notify({
      type: 'info',
      message: '请先选择一个操作，再进行图像处理',
      position: 'top',
      timeout: 3000
    });
  } else {
    $q.notify({
      type: 'warning',
      message: '未找到有效的图像处理操作，请检查系统配置',
      position: 'top',
      timeout: 5000
    });
  }
  
  // 然后加载相机列表
  await loadCameras()
  
  // 定期刷新相机状态
  setInterval(loadCameras, 10000)
})

// 组件卸载时
onBeforeUnmount(() => {
  // 停止所有活动的处理
  if (processingStream.value) {
    stopStreamProcessing()
  }
  
  // 清理自动检测计时器
  if (autoDetectInterval) {
    clearInterval(autoDetectInterval)
  }
  
  // 清理检测结果中的图片URL
  if (detectionResult.value?.imageData) {
    URL.revokeObjectURL(detectionResult.value.imageData)
  }
  
  // 清理批量处理结果
  batchResults.value.forEach(result => {
    if (result.processedImage && result.processedImage.startsWith('blob:')) {
      URL.revokeObjectURL(result.processedImage)
    }
  })
  
  // 重置所有状态
  isProcessingImage.value = false
  streamReady.value = false
  retryCount.value = 0
  batchResults.value = []
  batchProcessing.value = false
})

// 获取操作标签的函数
const getOperationName = (operationValue: string | null): string => {
  if (!operationValue || operationValue === 'none') return '无操作'
  
  const option = mergedOperationOptions.value.find(opt => opt.value === operationValue)
  if (!option) return '未知操作'
  
  return option.label
}

// 修改 onCapture 函数处理批量上传
const onCapture = async (result: any) => {
  // 检查是否为批量上传
  if (result.source === 'batch-upload' && result.batchImages) {
    await processBatchImages(result.batchImages)
    return
  }

  // 检查是否为上传的图片
  const isUploadedImage = result.source === 'upload'
  const captureSource = isUploadedImage ? '上传的图片' : '相机捕获'
  
  console.log(`处理${captureSource}图像`, result)
  
  // 检查是否选择了操作
  if (!selectedOperation.value || selectedOperation.value === 'none') {
    $q.notify({
      type: 'warning',
      message: t('realtime.notifications.selectOperation'),
      position: 'top'
    })
    return
  }

  try {
    // 设置处理状态
    isProcessingImage.value = true
    
    // 显示加载指示器
    $q.loading.show({
      message: `正在处理${captureSource}...`,
      spinnerColor: 'primary',
      backgroundColor: 'dark',
    })

    // 获取操作信息
    const operationType = selectedOperation.value.startsWith('operation:') ? 'operation' : 'pipeline'
    const operationId = parseInt(selectedOperation.value.split(':')[1])

    if (isNaN(operationId)) {
      throw new Error('无效的操作ID')
    }

    // 保存原始图像数据
    let originalImageData = null
    if (isUploadedImage) {
      // 对于上传的图片，记录原始上传的图片
      originalImageData = result.imageData
    } else {
      // 对于摄像头捕获，先获取原始快照
      const camera = selectedCamera.value
      if (!camera) {
        throw new Error('未选择摄像头')
      }

      const cameraId = getCameraDeviceId(camera)
      try {
        // 获取原始快照，不应用任何操作
        const originalResponse = await axios.get(
          `${API_BASE_URL}/cameras/camera_${cameraId}/snapshot`,
          {
            // 不传操作参数，获取原始图像
            responseType: 'arraybuffer',
            timeout: 5000 // 5秒超时
          }
        )
        
        // 检查返回的是否是图像数据
        const contentType = originalResponse.headers['content-type']
        if (contentType === 'application/json') {
          // 如果返回的是 JSON，说明是错误信息
          const errorText = new TextDecoder().decode(originalResponse.data)
          const errorJson = JSON.parse(errorText)
          throw new Error(errorJson.message || '获取原始图像失败')
        }

        // 创建原始图像 URL
        const originalBlob = new Blob([originalResponse.data], { type: 'image/jpeg' })
        originalImageData = URL.createObjectURL(originalBlob)
        console.log('成功获取摄像头原始快照')
      } catch (error) {
        console.error('获取原始快照失败:', error)
        // 如果获取原始快照失败，继续处理但不保存原始图像
      }
    }
    
    // 定义响应变量
    let response: any;
    
    // 定义处理结果变量
    let processedImageUrl = '';
    let detectedText = '';
    let confidence = 0;
    let isPassed = false;
    
    if (isUploadedImage) {
      // 处理上传的图片
      const formData = new FormData()
      // 从 base64 转换为 blob
      const base64Data = result.imageData.split(',')[1]
      const blob = await fetch(`data:image/jpeg;base64,${base64Data}`).then(r => r.blob())
      formData.append('image', blob, result.fileName || 'image.jpg')
      formData.append('operation_id', operationId.toString())
      formData.append('operation_type', operationType)
      
      response = await axios.post(
        `${API_BASE_URL}/cameras/process-image`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          // 对于上传图片处理，返回的是JSON数据
          responseType: 'json'
        }
      )
      
      // 上传图片处理返回的是JSON数据
      const responseData = response.data
      
      // 提取图片数据 - 这是处理后的图片
      processedImageUrl = responseData.image
      
      // 提取识别文字和置信度
      detectedText = responseData.text || ''
      confidence = responseData.confidence || 0
      isPassed = responseData.passed || false
      
      console.log('图片处理结果:', {
        text: detectedText,
        confidence: confidence,
        passed: isPassed
      })
      
      // 显示处理结果预览 - 使用处理后的图片
      processedResult.value = {
        imageData: processedImageUrl,
        operation: selectedOperation.value
      }
      
      // 确保上传图片状态保持，防止处理后原始图片消失
      uploadedImage.value = true
    } else {
      // 获取处理后的摄像头快照
      const camera = selectedCamera.value
      if (!camera) {
        throw new Error('未选择摄像头')
      }

      const cameraId = getCameraDeviceId(camera)
      
      try {
        // 请求后端API，传入return_json=true，使用JSON格式获取结果
        response = await axios.get(
          `${API_BASE_URL}/cameras/camera_${cameraId}/snapshot`,
          {
            params: {
              operation_id: operationId,
              operation_type: operationType,
              return_json: true  // 明确请求JSON格式的响应
            },
            responseType: 'json',  // 改为json，因为我们期望接收JSON对象
            timeout: 10000 // 10秒超时
          }
        )
        
        // 处理JSON响应
        const responseData = response.data
        
        // 提取处理后的图片数据
        processedImageUrl = responseData.image
        
        // 提取识别文字和置信度 - 注意：当前后端版本可能不返回这些数据
        detectedText = responseData.text || ''
        confidence = responseData.confidence || 0
        isPassed = responseData.passed || false
        
        // 检查是否有错误信息
        if (responseData.error) {
          console.warn('处理图像时发生错误:', responseData.error)
        }
        
        console.log('摄像头捕获处理结果:', {
          text: detectedText,
          confidence: confidence,
          passed: isPassed,
          错误: responseData.error || '无'
        })
        
        // 显示处理结果预览
        processedResult.value = {
          imageData: processedImageUrl,
          operation: selectedOperation.value
        }
      } catch (error) {
        console.warn('JSON格式获取失败，尝试使用二进制格式:', error)
        
        // 回退到旧版API方式，使用二进制响应
        response = await axios.get(
          `${API_BASE_URL}/cameras/camera_${cameraId}/snapshot`,
          {
            params: {
              operation_id: operationId,
              operation_type: operationType
            },
            responseType: 'arraybuffer',
            timeout: 10000 // 10秒超时
          }
        )
        
        // 检查是否是JSON格式的错误信息
        const contentType = response.headers['content-type']
        if (contentType === 'application/json') {
          // 如果返回的是 JSON，说明是错误信息
          const errorText = new TextDecoder().decode(response.data)
          const errorJson = JSON.parse(errorText)
          throw new Error(errorJson.message || '处理失败')
        }

        // 创建处理后图像 URL
        const imageBlob = new Blob([response.data], { type: 'image/jpeg' })
        processedImageUrl = URL.createObjectURL(imageBlob)
        
        // 旧版API不支持返回文字识别信息
        detectedText = ''
        confidence = 0
        isPassed = false
      }
    }

    // 更新检测结果
    detectionResult.value = {
      // 如果获取了原始图像，则使用原始图像作为历史记录中的原始图像
      imageData: originalImageData || processedImageUrl,
      // 添加处理后的图片数据
      processedImageData: processedImageUrl,
      timestamp: new Date(),
      passed: isPassed,
      text: detectedText,
      confidence: confidence,
      sourceType: captureSource,
      fileName: isUploadedImage ? result.fileName : undefined
    }

    // 保存检测结果
    await saveDetectionResult()

    $q.notify({
      type: 'positive',
      message: '图像处理完成',
      position: 'top'
    })
  } catch (error: any) {
    console.error('处理图像失败:', error)
    $q.notify({
      type: 'negative',
      message: `处理图像失败: ${error.message || '未知错误'}`,
      position: 'top'
    })
    
    // 更新检测结果以显示错误
    detectionResult.value = {
      timestamp: new Date(),
      passed: false,
      text: '',
      confidence: 0,
      sourceType: captureSource,
      errorReason: error.message || '未知错误'
    }
  } finally {
    isProcessingImage.value = false
    $q.loading.hide()
  }
}

// 处理批量图片
const processBatchImages = async (batchImages: {imageData: string, fileName: string}[]) => {
  // 检查是否选择了操作
  if (!selectedOperation.value || selectedOperation.value === 'none') {
    $q.notify({
      type: 'warning',
      message: t('realtime.notifications.selectOperation'),
      position: 'top'
    })
    return
  }

  // 清空之前的批量结果
  batchResults.value = []
  batchProcessing.value = true
  batchProgress.value = 0
  totalBatchImages.value = batchImages.length
  
  // 获取操作信息
  const operationType = selectedOperation.value.startsWith('operation:') ? 'operation' : 'pipeline'
  const operationId = parseInt(selectedOperation.value.split(':')[1])

  if (isNaN(operationId)) {
    $q.notify({
      type: 'negative',
      message: '无效的操作ID',
      position: 'top'
    })
    batchProcessing.value = false
    return
  }

  $q.loading.show({
    message: `正在批量处理图片 (0/${batchImages.length})...`,
    spinnerColor: 'primary',
    backgroundColor: 'dark',
  })

  try {
    // 逐个处理图片
    for (let i = 0; i < batchImages.length; i++) {
      const imageData = batchImages[i]
      
      // 更新进度
      batchProgress.value = Math.round(((i + 1) / batchImages.length) * 100)
      
      // 使用新的loading show代替update
      $q.loading.hide()
      $q.loading.show({
        message: `正在批量处理图片 (${i + 1}/${batchImages.length})...`,
        spinnerColor: 'primary',
        backgroundColor: 'dark',
      })
      
      try {
        // 处理单张图片
        const formData = new FormData()
        // 从 base64 转换为 blob
        const base64Data = imageData.imageData.split(',')[1]
        const blob = await fetch(`data:image/jpeg;base64,${base64Data}`).then(r => r.blob())
        formData.append('image', blob, imageData.fileName || 'image.jpg')
        formData.append('operation_id', operationId.toString())
        formData.append('operation_type', operationType)
        
        const response = await axios.post(
          `${API_BASE_URL}/cameras/process-image`,
          formData,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
            responseType: 'json'
          }
        )
        
        const responseData = response.data
        
        // 添加到结果列表
        batchResults.value.push({
          originalImage: imageData.imageData,
          processedImage: responseData.image,
          text: responseData.text || '',
          confidence: responseData.confidence || 0,
          passed: responseData.passed || false,
          fileName: imageData.fileName,
          timestamp: new Date(),
          error: null
        })
        
        // 如果是第一张图片，也显示在主结果区域
        if (i === 0) {
          // 更新检测结果
          detectionResult.value = {
            imageData: imageData.imageData,
            processedImageData: responseData.image,
            timestamp: new Date(),
            passed: responseData.passed || false,
            text: responseData.text || '',
            confidence: responseData.confidence || 0,
            sourceType: '批量上传',
            fileName: imageData.fileName
          }
          
          // 显示处理结果预览
          processedResult.value = {
            imageData: responseData.image,
            operation: selectedOperation.value
          }
        }
        
        // 保存检测结果到历史记录
        await detectionService.saveDetectionResult({
          text: responseData.text || '',
          confidence: responseData.confidence || 0,
          passed: responseData.passed || false,
          imageData: imageData.imageData,
          processedImageData: responseData.image,
          operationId: operationId,
          operationType: operationType
        })
      } catch (error: any) {
        console.error(`处理图片 ${imageData.fileName} 失败:`, error)
        
        // 添加错误结果
        batchResults.value.push({
          originalImage: imageData.imageData,
          processedImage: null,
          text: '',
          confidence: 0,
          passed: false,
          fileName: imageData.fileName,
          timestamp: new Date(),
          error: error.message || '处理失败'
        })
      }
    }
    
    // 完成处理
    $q.notify({
      type: 'positive',
      message: `批量处理完成，共处理 ${batchImages.length} 张图片`,
      position: 'top'
    })
    
    // 确保上传图片状态保持
    uploadedImage.value = true
  } catch (error: any) {
    console.error('批量处理图片失败:', error)
    $q.notify({
      type: 'negative',
      message: `批量处理失败: ${error.message || '未知错误'}`,
      position: 'top'
    })
  } finally {
    batchProcessing.value = false
    $q.loading.hide()
  }
}

// 添加流就绪处理函数
const handleStreamReady = () => {
  console.log('相机流已就绪')
  streamReady.value = true
  retryCount.value = 0
}

// 修改流错误处理函数
const handleStreamError = async (error: any) => {
  console.error('相机流错误:', error)
  
  // 如果超过最大重试次数，停止重试
  if (retryCount.value >= MAX_RETRIES) {
    $q.notify({
      type: 'negative',
      message: '相机流连接失败，请检查相机状态',
      position: 'top'
    })
    return
  }
  
  // 增加重试计数
  retryCount.value++
  
  // 等待一段时间后重试
  await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
  
  // 如果相机仍然选中，尝试重新连接
  if (selectedCamera.value) {
    console.log(`尝试重新连接相机 (${retryCount.value}/${MAX_RETRIES})`)
    // 重新加载相机
    await loadCameras()
  }
}

// 添加保存检测结果的函数
const saveDetectionResult = async () => {
  if (!detectionResult.value) return
  
  try {
    // 获取设备信息
    let deviceId = undefined
    
    if (selectedCamera.value) {
      // 使用数据库ID作为设备ID（这与摄像头设备ID不同）
      deviceId = selectedCamera.value.id
    }
    
    console.log('保存检测结果到历史记录:', {
      原始图像: detectionResult.value.imageData ? '已提供' : '未提供',
      处理后图像: detectionResult.value.processedImageData ? '已提供' : '未提供',
      备用处理图像: processedResult.value?.imageData ? '已提供' : '未提供'
    })
    
    await detectionService.saveDetectionResult({
      text: detectionResult.value.text || '',
      confidence: detectionResult.value.confidence || 0,
      passed: detectionResult.value.passed || false,
      imageData: detectionResult.value.imageData,
      processedImageData: detectionResult.value.processedImageData || processedResult.value?.imageData,
      deviceId: deviceId, // 使用数据库中的设备ID，而非摄像头设备ID
      operationId: selectedOperation.value ? parseInt(selectedOperation.value.split(':')[1]) : undefined,
      operationType: selectedOperation.value ? 
                    (selectedOperation.value.startsWith('operation:') ? 'operation' : 'pipeline') : 
                    undefined
    })
    
    console.log('检测结果已保存到历史记录')
  } catch (error) {
    console.error('保存检测结果失败:', error)
  }
}

// 添加相机错误处理方法
const onCameraError = (error: any) => {
  console.error('相机错误:', error)
  $q.notify({
    type: 'negative',
    message: `相机错误: ${error.message || '未知错误'}`,
    position: 'top'
  })
}

const emit = defineEmits(['camera-status-change'])

// 处理图像函数
const processImage = async () => {
  // 检查是否选择了操作
  if (!selectedOperation.value || selectedOperation.value === 'none') {
    $q.notify({
      type: 'warning',
      message: t('realtime.notifications.selectOperation'),
      position: 'top'
    })
    return
  }
  
  // 允许上传图片或使用相机捕获
  if (!isStreaming.value && !uploadedImage.value) {
    $q.notify({
      type: 'warning',
      message: t('realtime.notifications.uploadImage'),
      position: 'top'
    })
    
    // 触发CameraCapture组件的上传功能
    const cameraEl = document.querySelector('.camera-capture')
    if (cameraEl) {
      const uploadBtn = cameraEl.querySelector('button[label="上传图片"]')
      if (uploadBtn) {
        (uploadBtn as HTMLButtonElement).click()
      }
    }
    return
  }
  
  console.log('执行图像处理')
  
  // 通过触发CameraCapture组件的拍照按钮来实现
  const cameraEl = document.querySelector('.camera-capture')
  if (cameraEl) {
    // 如果是相机流模式，寻找拍照按钮
    if (isStreaming.value) {
      const captureBtn = cameraEl.querySelector('button[label="拍照"]')
      if (captureBtn) {
        (captureBtn as HTMLButtonElement).click()
      } else {
        throw new Error(t('realtime.notifications.noCameraControl'))
      }
    } 
    // 如果是上传的图片模式，触发处理按钮
    else if (uploadedImage.value) {
      const processBtn = cameraEl.querySelector('button[label="使用此图片处理"]')
      if (processBtn) {
        (processBtn as HTMLButtonElement).click()
      } else {
        throw new Error(t('realtime.notifications.noCameraControl'))
      }
    }
  } else {
    throw new Error(t('realtime.notifications.noCameraControl'))
  }
}

// 启动处理流函数
const startStream = async () => {
  if (!selectedCamera.value || !selectedOperation.value) {
    throw new Error(t('realtime.notifications.invalidOperation'))
  }

  $q.loading.show({
    message: t('realtime.notifications.startProcessing'),
    spinnerColor: 'primary',
    backgroundColor: 'dark',
  })

  try {
    // 获取操作信息
    const selectedOp = mergedOperationOptions.value.find(opt => opt.value === selectedOperation.value)
    if (!selectedOp) {
      throw new Error(t('realtime.notifications.invalidOperation'))
    }
    
    // 确定操作类型和ID
    const operationType = selectedOperation.value.startsWith('operation:') ? 'operation' : 'pipeline'
    const operationId = parseInt(selectedOperation.value.split(':')[1])
    
    if (isNaN(operationId)) {
      throw new Error(t('realtime.notifications.invalidOperation'))
    }
    
    // 获取摄像头ID
    const cameraId = getCameraDeviceId(selectedCamera.value)
    console.log('使用摄像头设备ID:', cameraId)
    
    // 构建处理流URL
    const streamUrl = cameraService.getCameraStreamUrl(
      cameraId,
      {
        operation_id: operationId,
        operation_type: operationType
      }
    ) + `&_t=${new Date().getTime()}`
    
    // 重置状态
    processedStreamRetryCount = 0
    processedStreamFirstLoaded = false
    
    // 更新UI状态
    processingStream.value = true
    processedStreamUrl.value = streamUrl
    
    console.log('处理流URL:', processedStreamUrl.value)
  } finally {
    $q.loading.hide()
  }
}
</script>

<style lang="scss" scoped>
.realtime-page {
  background: var(--dark-page);
}

.camera-card,
.result-card,
.control-card,
.operation-card,
.processed-card,
.batch-results-card {
  background: var(--dark-card);
}

.processed-image-container {
  width: 100%;
  max-height: 200px;
  overflow: hidden;
  border-radius: 4px;
  background: #111;
  display: flex;
  justify-content: center;
  align-items: center;
}

.processed-image {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.result-container {
  .text-h5 {
    padding: 1rem;
    border-radius: 8px;
    
    &.text-positive {
    background: rgba(46, 125, 50, 0.1);
    }
    
    &.text-negative {
      background: rgba(211, 47, 47, 0.1);
    }
  }
}

.no-result-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
}

// 添加视频显示相关样式
.view-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--q-primary);
}

.source-preview {
  height: 100%;
  width: 100%;
}

.processed-stream-container {
  width: 100%;
  aspect-ratio: 16/9;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.processed-stream {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: opacity 0.3s ease;
  
  &:hover {
    cursor: pointer;
  }
  
  &.loading {
    opacity: 0.5;
  }
}

.no-stream-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  
  .q-spinner {
    margin-bottom: 1rem;
  }
}

.stream-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  
  .q-badge {
    padding: 0.5rem 1rem;
    border-radius: 4px;
  }
}

// 添加批量处理相关样式
.batch-image-container {
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: 4px;
  background: #1a1a1a;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.batch-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.batch-error-container {
  width: 100%;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(211, 47, 47, 0.2);
  border-radius: 4px;
  border: 1px solid rgba(211, 47, 47, 0.3);
}

.batch-summary {
  .q-card {
    transition: all 0.3s;
    border: 1px solid rgba(255, 255, 255, 0.1);
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255, 255, 255, 0.15);
    }
  }
}
</style>