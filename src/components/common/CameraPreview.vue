<template>
  <div class="camera-preview">
    <div v-if="loading" class="camera-loading">
      <q-spinner color="primary" size="3em" />
      <div class="q-mt-sm">{{ t('cameraPreview.loading') }}</div>
    </div>
    <div v-else-if="error" class="camera-error">
      <q-icon name="error" color="negative" size="3em" />
      <div class="q-mt-sm">{{ errorMessage }}</div>
    </div>
    <img 
      ref="cameraImg" 
      :src="streamUrl" 
      :alt="t('cameraPreview.stream.alt')" 
      @error="handleStreamError" 
      @load="handleStreamLoaded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useI18n } from 'vue-i18n';
import { cameraService } from '../../services/camera';

const { t } = useI18n();

// Props
const props = defineProps<{
  cameraId: string;
  showControls?: boolean;
  directUrl?: string;
}>();

// Emits
const emit = defineEmits(['status-change']);

// 状态
const loading = ref(true);
const error = ref(false);
const errorMessage = ref('');
const cameraImg = ref<HTMLImageElement | null>(null);
const status = ref<'online' | 'offline' | 'error'>('offline');

// 计算属性
const streamUrl = computed(() => {
  // 如果设备配置指定了direct_url，直接使用
  if (props.directUrl) {
    return props.directUrl;
  }
  
  // 否则使用系统流地址
  return `${cameraService.getCameraStreamUrl(props.cameraId)}?t=${Date.now()}`;
});

// 处理流加载成功
const handleStreamLoaded = () => {
  loading.value = false;
  error.value = false;
  status.value = 'online';
  emit('status-change', 'online');
};

// 处理流加载错误
const handleStreamError = () => {
  loading.value = false;
  error.value = true;
  errorMessage.value = t('cameraPreview.error.connection');
  status.value = 'offline';
  emit('status-change', 'offline');
};

// 定期检查摄像头状态
let statusCheckInterval: number | null = null;

onMounted(() => {
  // 每10秒检查一次状态
  statusCheckInterval = window.setInterval(async () => {
    try {
      const statusResult = await cameraService.getCameraStatus(props.cameraId);
      status.value = statusResult.status as any;
      emit('status-change', status.value);
    } catch (e) {
      console.error(t('cameraPreview.error.status'), e);
    }
  }, 10000);
});

onBeforeUnmount(() => {
  if (statusCheckInterval !== null) {
    clearInterval(statusCheckInterval);
  }
});
</script>

<style scoped>
.camera-preview {
  width: 100%;
  aspect-ratio: 16/9;
  position: relative;
  overflow: hidden;
  background-color: #222;
  border-radius: 8px;
}

.camera-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-loading, .camera-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: white;
}
</style> 