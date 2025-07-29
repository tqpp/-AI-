<template>
  <div class="model-tester">
    <div class="row q-col-gutter-md">
      <!-- 测试控制区域 -->
      <div class="col-12 col-md-4">
        <!-- 选择模型区域 -->
        <div v-if="!selectedModel" class="select-model-card">
          <q-icon name="photo_camera" size="3em" color="primary" />
          <div class="text-h6 q-mt-md">{{ t('modelTester.selectModel.title') }}</div>
          <div class="text-body2 q-mt-sm text-grey">
            {{ t('modelTester.selectModel.hint') }}
          </div>
        </div>

        <!-- 控制面板 -->
        <div v-else class="control-panel">
          <div class="text-h6 q-mb-sm">{{ selectedModel.name }}</div>
          <div class="text-caption q-mb-md">{{ t('modelTester.model.id') }}: {{ selectedModel.id }}</div>

          <q-separator class="q-my-md" />

          <!-- 参数设置 -->
          <div class="text-subtitle1 q-mb-sm">{{ t('modelTester.params.title') }}</div>
          <q-input 
            v-model.number="confThreshold" 
            type="number" 
            :label="t('modelTester.params.confThreshold')" 
            outlined 
            dense 
            min="0" 
            max="1" 
            step="0.05"
          />
          <q-input 
            v-model.number="iouThreshold" 
            type="number" 
            :label="t('modelTester.params.iouThreshold')" 
            outlined 
            dense 
            min="0" 
            max="1" 
            step="0.05"
            class="q-mt-sm"
          />

          <q-separator class="q-my-md" />

          <!-- 图像上传 -->
          <div class="text-subtitle1 q-mb-sm">{{ t('modelTester.image.title') }}</div>
          <q-file
            v-model="imageFile"
            :label="t('modelTester.image.select')"
            outlined
            dense
            accept=".jpg,.jpeg,.png"
            @update:model-value="handleImageSelected"
          >
            <template v-slot:prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>

          <div class="q-mt-md">
            <q-btn 
              :label="t('modelTester.image.test')" 
              color="primary" 
              icon="science"
              @click="testModel"
              :loading="loading"
              :disable="!imageFile || loading"
              class="full-width"
            />
          </div>
        </div>
      </div>

      <!-- 测试结果区域 -->
      <div class="col-12 col-md-8">
        <q-card class="result-card">
          <q-card-section>
            <div class="text-h6">{{ t('modelTester.result.title') }}</div>

            <!-- 无图像时显示提示 -->
            <div v-if="!previewUrl && !resultImage" class="no-image-container">
              <q-icon name="insert_photo" size="4em" color="grey-5" />
              <div class="text-body1 q-mt-sm text-grey-7">
                {{ t('modelTester.result.noImage') }}
              </div>
            </div>

            <!-- 预览上传的图像 -->
            <div v-else-if="previewUrl && !resultImage" class="image-preview">
              <img :src="previewUrl" :alt="t('modelTester.result.preview')" />
            </div>

            <!-- 显示检测结果 -->
            <div v-else-if="resultImage" class="result-preview">
              <img :src="resultImage" :alt="t('modelTester.result.detectionResult')" />
              
              <div class="detection-list q-mt-md" v-if="detections && detections.length > 0">
                <div class="text-subtitle1 q-mb-sm">{{ t('modelTester.result.detectedObjects') }}</div>
                <q-list bordered separator class="rounded-borders">
                  <q-item v-for="(detection, index) in detections" :key="index">
                    <q-item-section avatar>
                      <q-avatar color="primary" text-color="white">
                        {{ index + 1 }}
                      </q-avatar>
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ detection.class_name }}</q-item-label>
                      <q-item-label caption>
                        {{ t('modelTester.result.confidence') }}: {{ (detection.confidence * 100).toFixed(1) }}%
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-badge color="primary">
                        {{ detection.class_id }}
                      </q-badge>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
              
              <div class="no-detection q-mt-md" v-else>
                <q-icon name="info" color="info" />
                <span class="q-ml-sm">{{ t('modelTester.result.noDetection') }}</span>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useI18n } from 'vue-i18n';
import { modelService, Model } from '../../services/model';

const { t } = useI18n();
const $q = useQuasar();

interface Props {
  selectedModel: Model | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update:selectedModel': [model: Model | null]
}>();

// 状态变量
const imageFile = ref<File | null>(null);
const previewUrl = ref<string | null>(null);
const loading = ref(false);
const confThreshold = ref(0.25);
const iouThreshold = ref(0.45);
const resultImage = ref<string | null>(null);
const detections = ref<any[] | null>(null);
const error = ref<string | null>(null);

// 图像选择处理
const handleImageSelected = (file: File | null) => {
  if (!file) {
    previewUrl.value = null;
    return;
  }

  // 创建图像预览
  const reader = new FileReader();
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string;
  };
  reader.readAsDataURL(file);
  
  // 重置测试结果
  resultImage.value = null;
  detections.value = null;
  error.value = null;
};

// 测试模型
const testModel = async () => {
  if (!props.selectedModel || !imageFile.value) {
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    const imageBase64 = previewUrl.value;
    if (!imageBase64) {
      throw new Error(t('modelTester.notifications.noImageData'));
    }

    const result = await modelService.testModelWithBase64(props.selectedModel.id, imageBase64, {
      conf_thres: confThreshold.value,
      iou_thres: iouThreshold.value
    });

    if (result.success && result.image) {
      resultImage.value = result.image;
      detections.value = result.detections || [];
      
      if (detections.value.length === 0) {
        $q.notify({
          type: 'info',
          message: t('modelTester.notifications.noObjectsDetected'),
          position: 'top'
        });
      } else {
        $q.notify({
          type: 'positive',
          message: t('modelTester.notifications.detectionCount', { count: detections.value.length }),
          position: 'top'
        });
      }
    } else {
      error.value = result.error || t('modelTester.notifications.testFailed', { error: '' });
      $q.notify({
        type: 'negative',
        message: t('modelTester.notifications.testFailed', { error: error.value }),
        position: 'top'
      });
    }
  } catch (err: any) {
    error.value = err.message || t('modelTester.notifications.testError', { error: '' });
    $q.notify({
      type: 'negative',
      message: t('modelTester.notifications.testError', { error: error.value }),
      position: 'top'
    });
  } finally {
    loading.value = false;
  }
};

// 当模型改变时重置状态
watch(() => props.selectedModel, () => {
  imageFile.value = null;
  previewUrl.value = null;
  resultImage.value = null;
  detections.value = null;
  error.value = null;
  
  // 如果有模型，从模型参数中获取默认阈值
  if (props.selectedModel?.parameters) {
    confThreshold.value = props.selectedModel.parameters.conf_thres || 0.25;
    iouThreshold.value = props.selectedModel.parameters.iou_thres || 0.45;
  }
});
</script>

<style lang="scss" scoped>
.model-tester {
  padding: 8px;
}

.select-model-card,
.control-panel {
  background: var(--dark-card);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 250px;
  text-align: center;
}

.control-panel {
  align-items: stretch;
  text-align: left;
  justify-content: flex-start;
}

.result-card {
  background: var(--dark-card);
  border-radius: 8px;
  min-height: 450px;
}

.no-image-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 350px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.image-preview,
.result-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 16px;
  
  img {
    max-width: 100%;
    max-height: 350px;
    object-fit: contain;
    border-radius: 4px;
  }
}

.detection-list {
  width: 100%;
}

.no-detection {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  background: rgba(var(--q-info-rgb), 0.1);
  border-radius: 4px;
}
</style> 