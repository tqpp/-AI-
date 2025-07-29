<template>
  <div class="camera-capture">
    <div class="camera-preview">
      <img 
        ref="streamImageElement" 
        class="video-stream" 
        :src="streamUrl" 
        :alt="t('camera.capture.videoStream')" 
        @error="handleStreamError"
        @load="handleStreamLoaded"
        v-show="isStreaming || (!isStreaming && !uploadedImage)"
      />
      
      <div v-if="isLoading" class="loading-overlay">
        <q-spinner size="3em" color="primary" />
        <div class="q-mt-sm">{{ t('camera.capture.loading') }}</div>
      </div>
      
      <div v-if="streamError" class="error-overlay">
        <q-icon name="error" size="3em" color="negative" />
        <div class="q-mt-sm">{{ t('camera.capture.error') }}</div>
      </div>
      
      <!-- 显示上传的图片 -->
      <div v-if="uploadedImage" class="uploaded-image-preview">
        <img :src="uploadedImage" alt="上传的图片" class="uploaded-image" />
        <div class="uploaded-image-info">
          <q-badge color="secondary">{{ t('camera.capture.uploadedImage') }}</q-badge>
        </div>
      </div>
      
      <!-- 无相机提示 -->
      <div v-if="!props.streamUrl && !uploadedImage" class="no-camera-overlay">
        <q-icon name="cloud_upload" size="3em" color="primary" />
        <div class="q-mt-sm">{{ t('camera.capture.noCamera') }}</div>
      </div>
    </div>
    
    <div class="camera-controls">
      <q-btn-group spread>
        <!-- 有相机时的按钮组 -->
        <template v-if="props.streamUrl">
          <q-btn
            icon="videocam"
            :label="isStreaming ? t('camera.capture.stopMonitoring') : t('camera.capture.startMonitoring')"
            :color="isStreaming ? 'negative' : 'primary'"
            @click="toggleStream"
          />
          
          <!-- 预览状态显示拍照按钮 -->
          <q-btn v-if="isStreaming"
            icon="photo_camera"
            :label="t('camera.capture.capture')"
            color="secondary"
            @click="captureImage"
          />
          
          <!-- 停止预览状态显示上传文件按钮 -->
          <q-btn v-else
            icon="cloud_upload"
            :label="t('camera.capture.uploadImage')"
            color="secondary"
            @click="triggerFileUpload"
          />
        </template>
        
        <!-- 没有相机时只显示上传图片按钮 -->
        <template v-else>
          <q-btn
            icon="cloud_upload"
            :label="t('camera.capture.uploadImage')"
            color="primary"
            class="full-width"
            @click="triggerFileUpload"
          />
        </template>
      </q-btn-group>
      
      <div class="text-caption q-mt-sm text-grey-8">
        <span v-if="props.streamUrl">
          {{ t('camera.capture.streamStatus') }} {{ isStreaming ? t('camera.capture.streaming') : t('camera.capture.stopped') }}
        </span>
        <span v-else-if="uploadedImage">
          {{ t('camera.capture.uploadedImage') }}
        </span>
        <span v-else>
          {{ t('camera.capture.noCamera') }}
        </span>
      </div>
      
      <!-- 使用已上传的图片处理的按钮 -->
      <div v-if="uploadedImage" class="upload-actions q-mt-sm">
        <q-btn
          icon="auto_fix_high"
          :label="t('camera.capture.useUploadedImage')"
          color="primary"
          class="full-width"
          @click="useUploadedImage"
        />
        <q-btn
          icon="refresh"
          :label="t('camera.capture.reupload')"
          color="secondary"
          class="full-width q-mt-xs"
          flat
          @click="triggerFileUpload"
        />
      </div>
      
      <!-- 隐藏的文件上传输入 -->
      <input 
        type="file" 
        ref="fileInput" 
        accept="image/*" 
        multiple
        style="display:none" 
        @change="handleFileUpload" 
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'

const $q = useQuasar()
const { t } = useI18n()

// Props定义
const props = defineProps({
  streamUrl: {
    type: String,
    default: ''
  },
  detectionResult: {
    type: Object,
    default: null
  },
  isProcessing: {
    type: Boolean,
    default: false
  }
})

// 状态变量
const streamImageElement = ref<HTMLImageElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const isStreaming = ref(false)
const isLoading = ref(false)
const streamError = ref<string | null>(null)
const isManualToggle = ref(false)
const uploadedImage = ref<string | null>(null)

// 删除额外的处理变量，只保留基本状态
let processingFrames = false

// 事件
const emit = defineEmits(['capture', 'error', 'status-change', 'frame', 'stream-ready', 'stream-error'])

// 监听流URL的变化
watch(() => props.streamUrl, (newUrl, oldUrl) => {
  console.log('流URL改变:', oldUrl, '->', newUrl)
  
  // 如果是手动操作，忽略此次URL变化
  if (isManualToggle.value) {
    console.log('忽略URL变化，因为是手动操作')
    isManualToggle.value = false
    return
  }
  
  // URL自动变化的处理逻辑
  if (newUrl && !oldUrl) {
    console.log('新的流URL可用，启动预览')
    startStream()
  } else if (newUrl && oldUrl && newUrl !== oldUrl && isStreaming.value) {
    console.log('流URL已更改，重新启动预览')
    stopStream()
    setTimeout(() => startStream(), 100)
  } else if (!newUrl && oldUrl) {
    console.log('流URL变为空，停止预览')
    stopStream()
  }
}, { immediate: true })

// 监听处理状态变化
watch(() => props.isProcessing, (newVal) => {
  // 如果开始处理，发送处理中的状态
  if (newVal) {
    emit('status-change', 'processing')
  } else {
    // 处理完成，但保持上传图片
    if (uploadedImage.value) {
      emit('status-change', 'uploaded')
    } else {
      emit('status-change', 'stopped')
    }
  }
})

// 处理流加载事件
const handleStreamLoaded = () => {
  console.log('视频流加载成功')
  
  // 确保当前URL不是空白图像
  const currentSrc = streamImageElement.value?.src || ''
  if (currentSrc === 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7') {
    console.log('忽略空白图像加载事件')
    return
  }
  
  isLoading.value = false
  isStreaming.value = true
  streamError.value = null
  
  // 清除已上传的图片
  uploadedImage.value = null
  
  // 通知父组件流已就绪
  emit('stream-ready')
  emit('status-change', 'online')
}

// 处理流错误事件
const handleStreamError = (event: Event) => {
  const currentSrc = streamImageElement.value?.src || ''
  const expectedUrl = props.streamUrl
  
  // 如果没有URL或正在显示空白图像，则不是真正的错误
  if (!expectedUrl || 
      currentSrc === 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7' || 
      !currentSrc.includes(expectedUrl)) {
    isLoading.value = false
    isStreaming.value = false
    return
  }
  
  // 正常错误处理
  isLoading.value = false
  isStreaming.value = false
  streamError.value = '加载视频流失败'
  
  // 发送错误事件，包含更多信息
  emit('stream-error', {
    message: '加载视频流失败',
    url: expectedUrl,
    currentSrc,
    timestamp: new Date().toISOString()
  })
  emit('status-change', 'error')
}

// 开启/关闭视频流
const toggleStream = () => {
  console.log('切换流状态，当前状态:', isStreaming.value)
  
  // 标记为手动操作
  isManualToggle.value = true
  
  if (isStreaming.value) {
    // 强制停止流
    console.log('强制停止流')
    isStreaming.value = false
    streamError.value = null
    
    if (streamImageElement.value) {
      streamImageElement.value.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
    }
    
    // 停止时触发状态变更
    emit('status-change', 'stopped')
  } else {
    // 强制开始流
    if (!props.streamUrl) {
      $q.notify({
        type: 'warning',
        message: '未提供视频流地址',
        position: 'top'
      })
      return
    }
    
    console.log('强制开始流')
    isLoading.value = true
    
    if (streamImageElement.value) {
      streamImageElement.value.src = props.streamUrl
    }
    
    // 清除上传的图片
    uploadedImage.value = null
    
    // 开始时触发状态变更
    emit('status-change', 'connecting')
  }
}

// 开启视频流
const startStream = () => {
  console.log('尝试开启视频流:', props.streamUrl)
  
  if (!props.streamUrl || props.streamUrl.trim() === '') {
    isLoading.value = false
    isStreaming.value = false
    streamError.value = '未提供视频流地址'
    
    console.log('未提供视频流地址或地址为空')
    emit('error', { message: '未提供视频流地址' })
    emit('status-change', 'error')
    return
  }
  
  isLoading.value = true
  streamError.value = null
  
  // 虽然不更新设备状态，但是UI上应该显示为正在连接
  // emit('status-change', 'connecting')
  
  if (streamImageElement.value) {
    // 设置流地址，事件处理器会处理加载完成和错误
    console.log('设置视频元素源:', props.streamUrl)
    streamImageElement.value.src = props.streamUrl
    
    // 清除上传的图片
    uploadedImage.value = null
  } else {
    console.log('视频元素未找到')
    isLoading.value = false
    streamError.value = '视频元素未找到'
    emit('error', { message: '视频元素未找到' })
    emit('status-change', 'error')
  }
}

// 停止视频流
const stopStream = () => {
  console.log('执行停止视频流')
  
  // 先更新状态，确保UI立即响应
  isStreaming.value = false
  streamError.value = null
  
  // 停止帧处理
  stopFrameProcessing()
  
  // 然后清空视频元素的src
  if (streamImageElement.value) {
    // 使用空白图像停止视频流
    console.log('清空视频源')
    streamImageElement.value.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
  }
  
  // 不发送status-change事件，避免将摄像头设为离线
  console.log('视频流已停止，isStreaming =', isStreaming.value)
}

// 拍照
const captureImage = () => {
  if (props.isProcessing) {
    $q.notify({
      type: 'warning',
      message: '正在处理中，请等待完成',
      position: 'top'
    })
    return
  }

  if (!isStreaming.value && !uploadedImage.value) {
    $q.notify({
      type: 'warning',
      message: '摄像头未就绪',
      position: 'top'
    })
    return
  }

  try {
    // 发出捕获事件，让父组件处理拍照逻辑
    emit('capture', {
      timestamp: new Date().toISOString(),
      source: 'camera'
    })
  } catch (error) {
    console.error('捕获图像失败:', error)
    emit('error', { 
      message: '捕获图像失败',
      error: error instanceof Error ? error.message : String(error)
    })
  }
}

// 触发文件上传
const triggerFileUpload = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

// 使用上传的图片
const useUploadedImage = () => {
  if (!uploadedImage.value) {
    $q.notify({
      type: 'warning',
      message: '没有上传的图片',
      position: 'top'
    })
    return
  }
  
  // 重新发送捕获事件，让父组件知道要处理这张图片
  emit('capture', {
    imageData: uploadedImage.value,
    timestamp: new Date().toISOString(),
    resolution: {
      width: 0, // 尺寸会在图片加载后确定
      height: 0
    },
    source: 'upload',
    fileName: 'reprocessed-image.png' // 使用固定文件名
  })
  
  $q.notify({
    type: 'positive',
    message: '图片准备好进行处理',
    position: 'top'
  })
}

// 处理文件上传
const handleFileUpload = (event: Event) => {
  if (props.isProcessing) {
    $q.notify({
      type: 'warning',
      message: '正在处理中，请等待完成',
      position: 'top'
    })
    return
  }

  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  
  // 检查所有文件是否都是图片
  const files = Array.from(target.files)
  const invalidFiles = files.filter(file => !file.type.includes('image/'))
  
  if (invalidFiles.length > 0) {
    $q.notify({
      type: 'negative',
      message: '请只上传图片文件',
      position: 'top'
    })
    return
  }
  
  // 对于批量上传，我们先通知用户
  if (files.length > 1) {
    $q.notify({
      type: 'info',
      message: `正在准备处理 ${files.length} 张图片`,
      position: 'top'
    })
  }
  
  try {
    // 对于单个文件，保持原有行为
    if (files.length === 1) {
      const file = files[0]
    const reader = new FileReader()
    reader.onload = (e) => {
      if (e.target && typeof e.target.result === 'string') {
        // 停止当前流，如果有的话
        if (isStreaming.value) {
          stopStream()
        }
        
        // 显示上传的图片
        uploadedImage.value = e.target.result
        
        // 发出捕获事件
        emit('capture', {
          imageData: e.target.result,
          timestamp: new Date().toISOString(),
          source: 'upload',
          fileName: file.name
        })
        
        // 更新状态
        emit('status-change', 'uploaded')
        
        // 重置文件输入
        if (fileInput.value) {
          fileInput.value.value = ''
        }
      }
    }
    
    reader.onerror = () => {
      emit('error', { 
        message: '图片读取失败',
        fileName: file.name,
        error: reader.error ? reader.error.message : '未知错误'
      })
    }
    
    reader.readAsDataURL(file)
    } 
    // 对于多个文件，发送批量上传事件
    else {
      // 停止当前流，如果有的话
      if (isStreaming.value) {
        stopStream()
      }
      
      // 对每个文件读取为base64，并收集结果
      const processFilesSequentially = async () => {
        const fileDataArray: {imageData: string, fileName: string}[] = []
        
        for (const file of files) {
          const base64Data = await new Promise<string>((resolve, reject) => {
            const reader = new FileReader()
            reader.onload = (e) => {
              if (e.target && typeof e.target.result === 'string') {
                resolve(e.target.result)
              } else {
                reject(new Error('无法读取图片数据'))
              }
            }
            reader.onerror = () => reject(reader.error)
            reader.readAsDataURL(file)
          })
          
          fileDataArray.push({
            imageData: base64Data,
            fileName: file.name
          })
        }
        
        // 显示第一张图片作为预览
        if (fileDataArray.length > 0) {
          uploadedImage.value = fileDataArray[0].imageData
        }
        
        // 发送批量上传事件
        emit('capture', {
          batchImages: fileDataArray,
          timestamp: new Date().toISOString(),
          source: 'batch-upload',
          count: fileDataArray.length
        })
        
        // 更新状态
        emit('status-change', 'uploaded')
        
        // 重置文件输入
        if (fileInput.value) {
          fileInput.value.value = ''
        }
      }
      
      processFilesSequentially().catch(error => {
        console.error('批量处理图片失败:', error)
        emit('error', { 
          message: '批量处理图片失败',
          error: error instanceof Error ? error.message : String(error)
        })
      })
    }
  } catch (error) {
    console.error('处理上传文件失败:', error)
    emit('error', { 
      message: '处理上传文件失败',
      error: error instanceof Error ? error.message : String(error)
    })
  }
}

// 简化帧处理开始函数
const startFrameProcessing = () => {
  console.log('通知后端开始帧处理')
  processingFrames = true
  
  // 触发状态变更
  emit('status-change', 'processing')
}

// 简化帧处理停止函数
const stopFrameProcessing = () => {
  console.log('通知后端停止帧处理')
  processingFrames = false
  
  // 触发状态变更
  emit('status-change', 'stopped')
}

// 组件挂载时
onMounted(() => {
  // 只有在提供了有效的流URL时才自动开始预览
  if (props.streamUrl && props.streamUrl.trim() !== '') {
    // 延迟启动预览，确保组件已完全渲染
    setTimeout(() => {
      startStream()
    }, 500)
  }
})

// 组件卸载时
onUnmounted(() => {
  // 确保停止所有活动
  stopStream()
  
  // 清理图片URL
  if (uploadedImage.value && uploadedImage.value.startsWith('blob:')) {
    URL.revokeObjectURL(uploadedImage.value)
  }
  
  // 重置所有状态
  isStreaming.value = false
  isLoading.value = false
  streamError.value = null
  uploadedImage.value = null
})
</script>

<style lang="scss" scoped>
.camera-capture {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--dark-page);
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

  .camera-preview {
    position: relative;
    width: 100%;
    aspect-ratio: 16/9;
    background: #000;
    border-radius: 4px;
    overflow: hidden;

    img.video-stream {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
    
    .loading-overlay,
    .error-overlay,
    .no-camera-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: rgba(0, 0, 0, 0.7);
      color: white;
      z-index: 10;
    }
    
    .error-overlay {
      background: rgba(150, 0, 0, 0.3);
    }
    
    .no-camera-overlay {
      background: rgba(0, 0, 0, 0.6);
    }
    
    .uploaded-image-preview {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #000;
      
      .uploaded-image {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
      }
      
      .uploaded-image-info {
        position: absolute;
        top: 8px;
        right: 8px;
        padding: 4px;
        border-radius: 4px;
        z-index: 20;
      }
    }
  }

  .camera-controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    
    .upload-actions {
      width: 100%;
      display: flex;
      flex-direction: column;
    }
  }
}
</style>