<template>
  <div class="text-region-annotator-container">
    <!-- 控制面板 -->
    <div class="controls-panel">
      <!-- 缩放控制 -->
      <q-btn round flat dense color="white" icon="remove" @click="zoomOut">
        <q-tooltip>{{ t('annotator.controls.zoomOut') }}</q-tooltip>
      </q-btn>

      <div class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</div>

      <q-btn round flat dense color="white" icon="add" @click="zoomIn">
        <q-tooltip>{{ t('annotator.controls.zoomIn') }}</q-tooltip>
      </q-btn>

      <div class="control-divider-vertical"></div>

      <!-- 文本区域标注按钮 -->
      <q-btn round flat dense :color="currentAnnotationType === 'text_region' && isDrawing ? 'negative' : 'white'"
        icon="polyline" @click="activateDrawingTool('text_region')">
        <q-tooltip>{{ t('annotator.tools.textRegion') }}</q-tooltip>
      </q-btn>

      <!-- 带字轮毂标注按钮 -->
      <q-btn round flat dense :color="currentAnnotationType === 'wheel_text' && isDrawing ? 'negative' : 'white'"
        icon="crop_square" @click="activateDrawingTool('wheel_text')">
        <q-tooltip>{{ t('annotator.tools.wheelText') }}</q-tooltip>
      </q-btn>

      <!-- 取消绘制按钮 -->
      <q-btn round flat dense color="negative" icon="close" @click="cancelDrawing" v-if="isDrawing">
        <q-tooltip>{{ t('annotator.controls.cancelDrawing') }}</q-tooltip>
      </q-btn>

      <div class="control-divider-vertical"></div>

      <!-- 删除按钮 -->
      <q-btn round flat dense color="white" icon="delete" @click="deleteSelected" :disable="!selectedAnnotation">
        <q-tooltip>{{ t('annotator.controls.deleteSelected') }}</q-tooltip>
      </q-btn>

      <!-- 保存按钮 -->
      <q-btn round flat dense color="white" icon="save" @click="saveAnnotations">
        <q-tooltip>{{ t('annotator.controls.save') }}</q-tooltip>
      </q-btn>

      <!-- 重新加载按钮 -->
      <q-btn round flat dense color="white" icon="refresh" @click="loadAnnotations">
        <q-tooltip>{{ t('annotator.controls.reload') }}</q-tooltip>
      </q-btn>
    </div>

    <!-- OpenSeadragon viewer container -->
    <div id="osd-container" ref="container" class="osd-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { useQuasar } from 'quasar'
import OpenSeadragon from 'openseadragon'
import { createOSDAnnotator } from '@annotorious/openseadragon'
import '@annotorious/openseadragon/annotorious-openseadragon.css'
import { AnnotationService } from '../../services/annotation'
import { useI18n } from 'vue-i18n'

// Get Quasar instance
const $q = useQuasar()
const { t } = useI18n()
const annotationService = new AnnotationService()

// Define props
interface Props {
  imageUrl: string
  imageId: number
  currentImage: {
    id: number
    url: string
    filename: string
  } | null
  scale?: number
}

const props = withDefaults(defineProps<Props>(), {
  scale: 1
})

// Define emits
const emit = defineEmits<{
  (e: 'update:annotations', annotations: any[]): void
  (e: 'annotationStatusChange', status: 'completed'): void
}>()

// Component refs
const container = ref<HTMLElement | null>(null)
const isDrawing = ref(false)
const zoomLevel = ref(1)
const selectedAnnotation = ref<any>(null)
const annotations = ref<any[]>([])
const lastSavedAnnotations = ref<string>('')
const currentAnnotationType = ref<'text_region' | 'wheel_text'>('text_region')

// OpenSeadragon and Annotorious instances
let viewer: any = null
let anno: any = null

// 标注类型配置
const annotationTypeConfig = {
  text_region: {
    tool: 'polygon',
    label: '文本区域',
    color: '#2196f3'
  },
  wheel_text: {
    tool: 'rectangle',
    label: '带字轮毂',
    color: '#ff9800'
  }
}

// 当前标注工具
const currentTool = computed(() => {
  return annotationTypeConfig[currentAnnotationType.value].tool
})

// Initialize OpenSeadragon and Annotorious
onMounted(() => {
  nextTick(() => {
    initializeViewer()
  })
})

// Clean up on component unmount
onUnmounted(() => {
  if (anno) {
    anno.destroy()
  }

  if (viewer) {
    viewer.destroy()
  }
})

// Initialize OpenSeadragon viewer and Annotorious
const initializeViewer = () => {
  if (!container.value) return

  if (viewer) {
    viewer.destroy()
  }
  if (anno) {
    anno.destroy()
  }
  // Initialize OpenSeadragon viewer
  viewer = OpenSeadragon({
    id: 'osd-container',
    tileSources: {
      type: 'image',
      url: props.imageUrl
    },
    showNavigationControl: false,
    zoomPerClick: 1,
    animationTime: 0.3,
    blendTime: 0.1,
    constrainDuringPan: true,
    maxZoomPixelRatio: 5,
    minZoomImageRatio: 0.8,
    visibilityRatio: 0.5,
    springStiffness: 10
  })

  // Initialize Annotorious with custom configuration
  anno = createOSDAnnotator(viewer, {
    style: (annotation: any, state: any) => {
      const label = annotation?.body?.find((b: any) => b.purpose === 'tagging')?.value;
      const color = label === 'text_region' ? '#ff0000' : '#ffffff';

      return {
        fill: color,
        fillOpacity: 0.4,
        stroke: color,
        strokeOpacity: 1
      }
    }
  })

  // Set default drawing tool
  anno.setDrawingTool(currentTool.value)

  // Set up event handlers
  setupEventHandlers()

  // Load annotations
  loadAnnotations()

  // Track zoom level
  viewer.addHandler('zoom', (event: any) => {
    zoomLevel.value = event.zoom
  })
}

// 获取标注类型
const getAnnotationType = (annotation: any): 'text_region' | 'wheel_text' => {
  if (!annotation || !annotation.body || !annotation.body.length) {
    return 'text_region' // 默认类型
  }

  const body = annotation.body.find((b: any) => b.purpose === 'tagging')
  if (body && body.value === 'wheel_text') {
    return 'wheel_text'
  }

  return 'text_region'
}

// 激活绘制工具
const activateDrawingTool = (type: 'text_region' | 'wheel_text') => {
  if (!anno) return

  // 如果已经是当前类型且正在绘制，则取消绘制
  if (currentAnnotationType.value === type && isDrawing.value) {
    cancelDrawing()
    return
  }

  // 设置当前标注类型
  currentAnnotationType.value = type

  // 设置绘制工具
  anno.setDrawingTool(annotationTypeConfig[type].tool)

  // 启用绘制
  anno.setDrawingEnabled(true)
  isDrawing.value = true

  // 取消选中
  if (selectedAnnotation.value) {
    selectedAnnotation.value = null
  }
}

// 取消绘制
const cancelDrawing = () => {
  if (!anno) return

  anno.setDrawingEnabled(false)
  isDrawing.value = false
}

// Set up Annotorious event handlers
const setupEventHandlers = () => {
  if (!anno) return

  // Handle annotation creation
  anno.on('createAnnotation', (annotation: any) => {
    console.log('Created annotation:', annotation)

    // 确保标注有正确的类型标签
    const hasTypeTag = annotation.body?.some((b: any) =>
      b.purpose === 'tagging' &&
      (b.value === 'text_region' || b.value === 'wheel_text')
    )

    if (!hasTypeTag) {
      // 添加当前类型的标签
      if (!annotation.body) annotation.body = []

      annotation.body.push({
        purpose: 'tagging',
        value: currentAnnotationType.value
      })
    }

    annotations.value.push(annotation)
    selectedAnnotation.value = annotation

    anno.updateAnnotation(annotation)
    // 创建后自动保存
    saveAnnotations()

    // 创建完成后禁用绘制模式
    isDrawing.value = false
    anno.setDrawingEnabled(false)
  })

  // Handle annotation updates
  anno.on('updateAnnotation', (annotation: any, previous: any) => {
    console.log('Updated annotation:', annotation, 'Previous:', previous)
    const index = annotations.value.findIndex(a => a.id === annotation.id)
    if (index !== -1) {
      annotations.value[index] = annotation
    }
    saveAnnotations()
  })

  // Handle annotation selection
  anno.on('selectionChanged', (selected: any) => {
    console.log('Selected annotation:', selected)
    selectedAnnotation.value = selected?.[0]

    // 如果选中了标注，自动切换到对应的标注类型
    if (selectedAnnotation.value) {
      const type = getAnnotationType(selectedAnnotation.value)
      currentAnnotationType.value = type

      // 如果正在绘制，则取消绘制
      if (isDrawing.value) {
        isDrawing.value = false
        anno.setDrawingEnabled(false)
      }
    }
  })
}

// Load annotations from the server
const loadAnnotations = async () => {
  try {
    const response = await annotationService.getImageAnnotation(props.imageId)
    console.log('Backend annotation data:', response)

    if (response?.annotations && Array.isArray(response.annotations)) {
      let annotatoriousAnnotations = response.annotations;
      console.log('Annotations for Annotorious:', annotatoriousAnnotations)

      // Load annotations into Annotorious
      if (anno && annotatoriousAnnotations.length > 0) {
        anno.setAnnotations(annotatoriousAnnotations)
      }

      // Update local state
      annotations.value = annotatoriousAnnotations
      lastSavedAnnotations.value = JSON.stringify(annotatoriousAnnotations)

      // Notify parent component
      emit('update:annotations', annotatoriousAnnotations)
    } else {
      // No annotations or invalid format
      annotations.value = []
      lastSavedAnnotations.value = '[]'

      if (anno) {
        anno.setAnnotations([])
      }
    }
  } catch (error) {
    console.error('Failed to load annotations:', error)
    $q.notify({
      type: 'negative',
      message: t('annotator.notifications.loadFailed'),
      position: 'top'
    })
  }
}

// Save annotations to the server
const saveAnnotations = async () => {
  try {
    if (!anno) return

    // Get current annotations from Annotorious
    const currentAnnotations = anno.getAnnotations()

    // Check if there are actual changes to save
    const currentJson = JSON.stringify(currentAnnotations)
    if (currentJson === lastSavedAnnotations.value) {
      console.log('No changes to save')
      return
    }

    // Save annotations directly in W3C format
    await annotationService.saveAnnotation(props.imageId, {
      annotations: currentAnnotations
    })

    // Update last saved state
    lastSavedAnnotations.value = currentJson

    // Notify parent component
    emit('update:annotations', currentAnnotations)
    emit('annotationStatusChange', 'completed')

    $q.notify({
      type: 'positive',
      message: t('annotator.notifications.saveSuccess'),
      position: 'top'
    })
  } catch (error) {
    console.error('Failed to save annotations:', error)
    $q.notify({
      type: 'negative',
      message: t('annotator.notifications.saveFailed'),
      position: 'top'
    })
  }
}

// Delete selected annotation
const deleteSelected = async () => {
  if (!anno || !selectedAnnotation.value) return

  try {
    const annotationId = selectedAnnotation.value.id

    // Remove from Annotorious
    anno.removeAnnotation(annotationId)

    // Update local state
    annotations.value = annotations.value.filter(ann => ann.id !== annotationId)
    selectedAnnotation.value = null

    // Save changes to backend
    await saveAnnotations()
  } catch (error) {
    console.error('Failed to delete annotation:', error)
    $q.notify({
      type: 'negative',
      message: t('annotator.notifications.deleteFailed'),
      position: 'top'
    })

    // Reload annotations to restore state
    loadAnnotations()
  }
}

// Zoom in
const zoomIn = () => {
  if (viewer) {
    viewer.viewport.zoomBy(1.2)
    viewer.viewport.applyConstraints()
  }
}

// Zoom out
const zoomOut = () => {
  if (viewer) {
    viewer.viewport.zoomBy(0.8)
    viewer.viewport.applyConstraints()
  }
}

// Watch for image changes
watch(() => props.imageUrl, (newUrl) => {
  if (newUrl && viewer) {
    initializeViewer()
  }
})
</script>

<style lang="scss" scoped>
.text-region-annotator-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #2b2b2b;
  border-radius: 8px;
  overflow: hidden;
}

.osd-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.controls-panel {
  position: absolute;
  top: 1px;
  right: 1px;
  z-index: 10;
  background: rgba(43, 43, 43, 0.5);
  padding: 0px 0px;
  border-radius: 8px;
  color: #fff;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.zoom-level {
  font-size: 14px;
  color: #e0e0e0;
  min-width: 40px;
  text-align: center;
}

.control-divider-vertical {
  width: 1px;
  height: 24px;
  background-color: rgba(255, 255, 255, 0.2);
  margin: 0 4px;
}

/* Override Annotorious styles for better integration */
:deep(.a9s-annotationlayer) {
  z-index: 1;
}

:deep(.a9s-annotation) {
  cursor: pointer;
}

:deep(.a9s-annotation.selected) {
  stroke: #00ff00 !important;
  stroke-width: 2px !important;
}

/* 为不同类型的标注设置不同的样式 */
:deep(.a9s-annotation[data-type="text_region"]) {
  stroke: #2196f3;
  stroke-width: 2px;
  fill: rgba(33, 150, 243, 0.2);
}

:deep(.a9s-annotation[data-type="wheel_text"]) {
  stroke: #ff9800;
  stroke-width: 2px;
  fill: rgba(255, 152, 0, 0.2);
}
</style>