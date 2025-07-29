<template>
    <q-dialog @keydown.esc="handleClose" :model-value="modelValue"
        @update:model-value="emit('update:modelValue', $event)" persistent maximized class="generate-data-dialog">
        <q-card class="generate-data-card">
            <q-card-section class="row items-center q-pb-none">
                <div class="text-h6">{{ t('generateData.title') }}</div>
                <q-space />
                <q-btn icon="close" flat round dense @click="handleClose" />
            </q-card-section>

            <q-card-section class="q-pt-sm">
                <div class="row q-col-gutter-md">
                    <!-- 左侧：源数据集信息 -->
                    <div class="col-12 col-md-3">
                        <q-card flat bordered>
                            <q-card-section>
                                <div class="text-subtitle1">{{ t('generateData.sourceDataset.title') }}</div>
                                <div class="text-caption q-mt-sm">
                                    <q-icon name="folder" color="primary" size="sm" />
                                    {{ sourceDataset.name }}
                                </div>
                                <div class="text-caption q-mt-xs">
                                    <q-icon name="image" color="primary" size="sm" />
                                    {{ sourceImages.length }} 张图片
                                </div>
                                <div class="text-caption q-mt-xs">
                                    <q-icon name="label" color="primary" size="sm" />
                                    {{ getAnnotatedCount() }} 张已标注
                                </div>
                            </q-card-section>

                            <q-separator />

                            <q-card-section>
                                <div class="text-subtitle1">{{ t('generateData.targetDataset.title') }}</div>
                                <q-option-group v-model="targetDatasetOption" :options="[
                                    { label: t('generateData.targetDataset.newOption'), value: 'new' },
                                    { label: t('generateData.targetDataset.existingOption'), value: 'existing' },
                                    { label: t('generateData.targetDataset.sourceOption'), value: 'source' }
                                ]" color="primary" />

                                <template v-if="targetDatasetOption === 'new'">
                                    <q-input v-model="newDatasetName" label="新数据集名称" class="q-mt-sm" dense
                                        :rules="[val => !!val || t('generateData.targetDataset.new.name.required')]" />
                                    <q-select 
                                        v-model="newDatasetType" 
                                        :options="datasetTypeOptions" 
                                        option-label="label"
                                        option-value="value"
                                        label="数据集类型"
                                        class="q-mt-sm" 
                                        dense 
                                    />
                                </template>

                                <template v-if="targetDatasetOption === 'existing'">
                                    <q-select v-model="selectedTargetDataset" :options="availableDatasets" label="选择数据集"
                                        option-label="name" option-value="id" class="q-mt-sm" dense
                                        :rules="[val => !!val || t('generateData.targetDataset.existing.select')]" />
                                </template>
                            </q-card-section>

                            <q-separator />

                            <q-card-section>
                                <div class="text-subtitle1">{{ t('generateData.generateOptions.title') }}</div>
                                <q-checkbox v-model="includeAnnotations" :label="t('generateData.generateOptions.includeAnnotations')" />
                                <div class="text-caption q-mt-xs">
                                    {{ t('generateData.generateOptions.includeAnnotationsHint') }}
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>

                    <!-- 中间：操作选择 -->
                    <div class="col-12 col-md-4">
                        <q-card flat bordered>
                            <q-card-section class="operations-section">
                                <div class="text-subtitle1">{{ t('generateData.operations.title') }}</div>
                                <!-- 可选操作列表 -->
                                <div class="text-caption q-mb-sm">{{ t('generateData.operations.available') }}</div>
                                <div class="available-operations">
                                    <!-- 单步处理操作 -->
                                    <q-chip v-for="op in filteredOperations" :key="'op-' + op.id" clickable
                                        class="operation-chip" @click="addInstance(op, 'operation')">
                                        {{ op.name }}
                                        <q-badge color="primary" class="q-ml-xs" floating>{{ t('generateData.operations.single') }}</q-badge>
                                        <q-tooltip v-if="op.description" anchor="bottom middle" self="center middle">
                                            {{ op.description }}
                                        </q-tooltip>
                                    </q-chip>

                                    <!-- 流水线处理操作 -->
                                    <q-chip v-for="pipeline in pipelines" :key="'pl-' + pipeline.id" clickable
                                        class="operation-chip" @click="addInstance(pipeline, 'pipeline')">
                                        {{ pipeline.name }}
                                        <q-badge color="purple" class="q-ml-xs" floating>{{ t('generateData.operations.pipeline') }}</q-badge>
                                        <q-tooltip v-if="pipeline.description" anchor="bottom middle" self="center middle">
                                            {{ pipeline.description }}
                                        </q-tooltip>
                                    </q-chip>
                                </div>
                                <q-separator />
                                <!-- 已选操作列表 -->
                                <div class="text-caption q-mb-sm">{{ t('generateData.operations.selected') }} ({{ selectedInstances.length }})</div>
                                <q-list separator>
                                    <q-item v-for="(instance, index) in selectedInstances" :key="instance.id">
                                        <q-item-section>
                                            <q-item-label>
                                                {{ instance.name }}
                                                <q-badge :color="instance.type === 'operation' ? 'primary' : 'purple'"
                                                    class="q-ml-sm">
                                                    {{ instance.type === 'operation' ? t('generateData.operations.single') : t('generateData.operations.pipeline') }}
                                                </q-badge>
                                            </q-item-label>
                                        </q-item-section>
                                        <q-item-section side>
                                            <div class="row items-center">
                                                <q-btn round flat dense icon="settings"
                                                    @click="configureInstance(instance)">
                                                    <q-tooltip>{{ t('generateData.operations.configure') }}</q-tooltip>
                                                </q-btn>
                                                <q-btn round flat dense icon="content_copy"
                                                    @click="duplicateInstance(instance)">
                                                    <q-tooltip>{{ t('generateData.operations.duplicate') }}</q-tooltip>
                                                </q-btn>
                                                <q-btn round flat dense icon="delete" @click="removeInstance(index)">
                                                    <q-tooltip>{{ t('generateData.operations.remove') }}</q-tooltip>
                                                </q-btn>
                                            </div>
                                        </q-item-section>
                                    </q-item>
                                </q-list>
                            </q-card-section>
                        </q-card>
                    </div>

                    <!-- 右侧：预览和生成 -->
                    <div class="col-12 col-md-5">
                        <q-card flat bordered>
                            <q-card-section>
                                <div class="text-subtitle1">{{ t('generateData.preview.title') }}</div>
                                <div class="preview-container">
                                    <div class="preview-pipeline" v-for="(preview, index) in previewImages" :key="index">
                                        <div class="pipeline-header">
                                            <q-badge color="primary" outline>
                                                {{ t('generateData.preview.sourceImage') }} #{{ index + 1 }}
                                            </q-badge>
                                            <span class="image-info">
                                                {{ t('generateData.preview.imageId', { id: preview.sourceImageId }) }}
                                            </span>
                                        </div>
                                        
                                        <div class="source-image-row">
                                            <!-- Original image -->
                                            <div class="source-image-container">
                                                <div class="stage-header">
                                                    <span class="stage-name">{{ t('generateData.preview.originalImage') }}</span>
                                                </div>
                                                <div class="stage-content">
                                                    <AnnotationPreview 
                                                        :imageUrl="preview.sourceImageUrl"
                                                        :annotations="preview.originalAnnotation"
                                                        height="160px"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <!-- Operation results for this image -->
                                        <div class="operation-results">
                                            <div 
                                                v-for="(operation, opIndex) in preview.operations" 
                                                :key="opIndex"
                                                class="operation-result"
                                            >
                                                <div class="operation-header">
                                                    <span class="operation-title">{{ operation.operationName }}</span>
                                                    <q-badge 
                                                        v-if="operation.operationType" 
                                                        :color="operation.operationType === 'operation' ? 'primary' : 'purple'"
                                                        class="q-ml-xs"
                                                    >
                                                        {{ t(`generateData.preview.operationResult.${operation.operationType === 'operation' ? 'single' : 'pipeline'}`) }}
                                                    </q-badge>
                                                </div>
                                                <div class="operation-content">
                                                    <AnnotationPreview 
                                                        :imageUrl="`data:image/png;base64,${operation.processedImage}`"
                                                        :annotations="operation.processedAnnotation"
                                                        height="160px"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </q-card-section>

                            <q-separator />

                            <q-card-section>
                                <div class="row q-col-gutter-sm">
                                    <div class="col">
                                        <q-btn color="primary" icon="visibility" :label="t('generateData.actions.preview')" 
                                            @click="generatePreview" :loading="previewLoading" :disable="!canPreview" />
                                    </div>
                                    <div class="col">
                                        <q-btn color="positive" icon="auto_awesome" :label="t('generateData.actions.generate')" 
                                            @click="generateData" :loading="generating" :disable="!canGenerate" />
                                    </div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </q-card-section>

            <!-- 生成进度对话框 -->
            <q-dialog v-model="showProgressDialog" persistent>
                <q-card style="min-width: 350px">
                    <q-card-section>
                        <div class="text-h6">{{ t('generateData.progress.title') }}</div>
                    </q-card-section>

                    <q-card-section>
                        <div class="text-body1 q-mb-md">
                            {{ progressStatus }}
                        </div>
                        <q-linear-progress :value="progressValue" color="primary" size="md" class="q-mb-sm" />
                        <div class="text-caption">
                            {{ progressText }}
                        </div>
                    </q-card-section>

                    <q-card-actions align="right">
                        <q-btn flat :label="t('generateData.progress.cancel')" color="negative" 
                            @click="cancelGeneration" :disable="!canCancelGeneration" v-if="generating" />
                        <q-btn flat :label="t('generateData.progress.close')" color="primary" 
                            @click="closeProgressDialog" v-if="!generating" />
                    </q-card-actions>
                </q-card>
            </q-dialog>

            <!-- 参数配置对话框 -->
            <q-dialog v-model="showConfigDialog" persistent>
                <q-card style="min-width: 400px; max-width: 600px">
                    <q-card-section>
                        <div class="text-h6">{{ t('generateData.configuration.title', { name: currentInstance?.name }) }}</div>
                    </q-card-section>

                    <q-card-section class="q-pt-none">
                        <div v-if="currentInstance">
                            <!-- 输入参数配置 -->
                            <div class="text-subtitle2 q-my-sm">{{ t('generateData.configuration.sections.input') }}</div>
                            <div v-for="param in currentInstance.inputParams" :key="param.name" class="q-mb-md">
                                <div class="text-subtitle2">{{ param.name }}</div>
                                <div class="text-caption q-mb-xs">{{ param.description }}</div>

                                <!-- 根据参数类型渲染不同的输入控件 -->
                                <template v-if="param.type === 'number'">
                                    <q-input v-model.number="currentInstance.params[param.name]" type="number" dense
                                        :label="param.required ? t('generateData.configuration.params.required') : t('generateData.configuration.params.optional')"
                                        :hint="t('generateData.configuration.params.defaultValue', { value: param.default })" />
                                </template>

                                <template v-else-if="param.type === 'text'">
                                    <q-input v-model="currentInstance.params[param.name]" dense
                                        :label="param.required ? t('generateData.configuration.params.required') : t('generateData.configuration.params.optional')"
                                        :hint="t('generateData.configuration.params.defaultValue', { value: param.default })" />
                                </template>

                                <template v-else-if="param.type === 'boolean'">
                                    <q-toggle v-model="currentInstance.params[param.name]" :label="param.name"
                                        :hint="t('generateData.configuration.params.defaultValue', { value: param.default ? t('generateData.configuration.params.yes') : t('generateData.configuration.params.no') })" />
                                </template>

                                <template v-else-if="param.type === ParamType.IMAGE">
                                    <div class="row items-center q-col-gutter-sm">
                                        <div class="col-12">
                                            <div class="text-caption q-mb-sm">
                                                <q-icon name="info" size="xs" color="info" class="q-mr-xs" />
                                                {{ t('generateData.configuration.imageParam.hint') }}
                                            </div>
                                            <q-radio 
                                                v-model="currentInstance.params[param.name]" 
                                                val="$IMAGE" 
                                                :label="t('generateData.configuration.imageParam.useDataset')"
                                                :disable="!isDatasetImageParam(param.name)"
                                            />
                                            <q-radio 
                                                v-model="currentInstance.params[param.name]" 
                                                val="custom" 
                                                :label="t('generateData.configuration.imageParam.upload')" 
                                            />
                                        </div>
                                        
                                        <div class="col-12" v-if="currentInstance.params[param.name] === 'custom'">
                                            <q-file
                                                v-model="currentInstance.params[`${param.name}_file`]"
                                                dense
                                                accept="image/*,.bmp"
                                                :label="param.required ? t('generateData.configuration.params.required') : t('generateData.configuration.params.optional')"
                                            >
                                                <template v-slot:prepend>
                                                    <q-icon name="image" />
                                                </template>
                                            </q-file>
                                        </div>
                                    </div>
                                </template>

                                <template v-else-if="param.type === ParamType.OBJECT">
                                    <div class="row items-center q-col-gutter-sm">
                                        <div class="col-12">
                                            <div class="text-caption q-mb-sm">
                                                <q-icon name="info" size="xs" color="info" class="q-mr-xs" />
                                                {{ t('generateData.configuration.annotationParam.hint') }}
                                            </div>
                                            <q-radio 
                                                v-model="currentInstance.params[param.name]" 
                                                val="$ANNOTATION" 
                                                :label="t('generateData.configuration.annotationParam.useDataset')"
                                                :disable="!isDatasetAnnotationParam(param.name)"
                                            />
                                            <q-radio 
                                                v-model="currentInstance.params[param.name]" 
                                                val="custom" 
                                                :label="t('generateData.configuration.annotationParam.custom')" 
                                            />
                                        </div>
                                        
                                        <div class="col-12" v-if="currentInstance.params[param.name] === 'custom'">
                                            <q-input
                                                v-model="currentInstance.params[`${param.name}_data`]"
                                                type="textarea"
                                                dense
                                                :label="param.required ? t('generateData.configuration.params.required') : t('generateData.configuration.params.optional')"
                                                :hint="t('generateData.configuration.annotationParam.customHint')"
                                            />
                                        </div>
                                    </div>
                                </template>
                            </div>

                            <!-- 输出参数配置 -->
                            <div class="text-subtitle2 q-my-sm">{{ t('generateData.configuration.sections.output') }}</div>
                            <div class="text-caption q-mb-sm">
                                <q-icon name="info" size="xs" color="info" class="q-mr-xs" />
                                {{ t('generateData.configuration.output.hint') }}
                            </div>

                            <!-- 图片输出参数选择 -->
                            <div class="q-mb-md">
                                <div class="text-weight-medium">{{ t('generateData.configuration.output.image.title') }}</div>
                                <q-option-group
                                    v-model="currentInstance.params.outputImageParam"
                                    :options="getParamsByType(ParamType.IMAGE, 'output').map(p => ({
                                        label: p.name + (p.description ? ` - ${p.description}` : ''),
                                        value: p.name
                                    }))"
                                    type="radio"
                                    color="primary"
                                    :disable="!hasImageOutput"
                                />
                                <div class="text-caption q-mt-xs" v-if="!hasImageOutput">
                                    {{ t('generateData.configuration.output.image.noOutput') }}
                                </div>
                            </div>

                            <!-- 标注输出参数选择 -->
                            <div class="q-mb-md">
                                <div class="text-weight-medium">{{ t('generateData.configuration.output.annotation.title') }}</div>
                                <q-option-group
                                    v-model="currentInstance.params.outputAnnotationParam"
                                    :options="getParamsByType(ParamType.OBJECT, 'output').map(p => ({
                                        label: p.name + (p.description ? ` - ${p.description}` : ''),
                                        value: p.name
                                    }))"
                                    type="radio"
                                    color="primary"
                                    :disable="!hasObjectOutput"
                                />
                                <div class="text-caption q-mt-xs" v-if="!hasObjectOutput">
                                    {{ t('generateData.configuration.output.annotation.noOutput') }}
                                </div>
                            </div>
                        </div>
                    </q-card-section>

                    <q-card-actions align="right">
                        <q-btn flat :label="t('generateData.configuration.actions.reset')" color="warning" @click="resetParams" />
                        <q-btn flat :label="t('generateData.configuration.actions.close')" color="primary" v-close-popup />
                    </q-card-actions>
                </q-card>
            </q-dialog>
        </q-card>
    </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, PropType } from 'vue'
import { useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'
import { AnnotationService, Dataset, DatasetType } from '../../services/annotation'
import type { Image } from '../../services/annotation'
import { CVOperation, CVOperationService, ParamType } from '../../services/cv_operation'
import { Pipeline, PipelineService } from '../../services/pipeline'
import { W3CAnnotation } from '@annotorious/openseadragon'
import AnnotationPreview from './AnnotationPreview.vue'

const { t } = useI18n()

// 在 OperationInstance 接口中添加参数映射
interface OperationInstance extends Partial<CVOperation>, Partial<Pipeline> {
    instanceId: number
    type: 'operation' | 'pipeline' | undefined
    params: Record<string, any>
}

const $q = useQuasar()
const annotationService = new AnnotationService()
const cvOperationService = new CVOperationService()
const pipelineService = new PipelineService()

// 属性定义
const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false
    },
    sourceDataset: {
        type: Object as PropType<Dataset>,
        required: true
    },
    sourceImages: {
        type: Array as PropType<Image[]>,
        default: () => []
    }
})

// 事件
const emit = defineEmits(['update:modelValue', 'update:datasets'])

// 数据集相关
const availableDatasets = ref<Dataset[]>([])
const targetDatasetOption = ref<'new' | 'existing' | 'source'>('source')
const newDatasetName = ref()
const newDatasetType = ref()
const selectedTargetDataset = ref<Dataset | null>(null)
const includeAnnotations = ref(true)

// 操作相关
const cvOperations = ref<CVOperation[]>([])
const pipelines = ref<Pipeline[]>([])


const selectedInstances = ref<OperationInstance[]>([])
let nextInstanceId = 1

// 预览相关
const previewLoading = ref(false)
const previewImages = ref<PreviewImage[]>([])

// 生成相关
const generating = ref(false)
const showProgressDialog = ref(false)
const progressValue = ref(0)
const progressText = ref('')
const progressStatus = ref('')
const canCancelGeneration = ref(true)

// 配置对话框
const showConfigDialog = ref(false)
const currentInstance = ref<OperationInstance | null>(null)
const paramValues = ref<Record<string, any>>({})

// 过滤出合适的操作（输入和输出都包含图片）
const filteredOperations = computed(() => {
    return cvOperations.value.filter(op => {
        // 检查输入参数是否包含图片类型
        const hasImageInput = op.inputParams.some(param =>
            param.type === ParamType.IMAGE || param.name.toLowerCase().includes(ParamType.IMAGE)
        )

        // 检查输出参数是否包含图片类型
        const hasImageOutput = op.outputParams.some(param =>
            param.type === ParamType.IMAGE || param.name.toLowerCase().includes(ParamType.IMAGE)
        )

        return hasImageInput && hasImageOutput
    })
})

// 是否可以预览
const canPreview = computed(() => {
    return selectedInstances.value.length > 0
})

// 是否可以生成
const canGenerate = computed(() => {
    if (!canPreview.value) return false

    if (targetDatasetOption.value === 'new') {
        return !!newDatasetName.value
    } else if (targetDatasetOption.value === 'existing') {
        return !!selectedTargetDataset.value
    }

    return true
})

// 获取已标注图片数量
const getAnnotatedCount = () => {
    return props.sourceImages.filter(img => img.isAnnotated).length
}

// 数据集类型选项
const datasetTypeOptions = [
    { label: t('annotation.datasetTypes.textRegion'), value: DatasetType.TEXT_REGION },
    { label: t('annotation.datasetTypes.ocr'), value: DatasetType.OCR }
]

// 加载数据
const loadData = async () => {
    try {
        // 加载可用数据集
        availableDatasets.value = await annotationService.getDatasets()

        // 加载CV操作
        cvOperations.value = await cvOperationService.getOperations()

        // 加载流水线
        pipelines.value = await pipelineService.getPipelines()

        // 设置默认值
        newDatasetName.value = `${props.sourceDataset.name}_生成`
        newDatasetType.value = datasetTypeOptions.find(option => option.value === props.sourceDataset.type)

    } catch (error) {
        console.error('加载数据失败:', error)
        $q.notify({
            type: 'negative',
            message: t('generateData.notifications.loadError'),
            position: 'top'
        })
    }
}

// 添加操作实例
const addInstance = (item: CVOperation | Pipeline, type: 'operation' | 'pipeline') => {
    const instance: OperationInstance = {
        instanceId: nextInstanceId++,
        ...item,
        params: {},
        type: type
    }

    // 设置默认参数
    let hasSetImage = false
    let hasSetAnnotation = false
    let hasSetOutputImage = false
    let hasSetOutputAnnotation = false

    item.inputParams.forEach(param => {
        if (param.type === ParamType.IMAGE && !hasSetImage) {
            // 第一个图片参数默认使用数据集图片
            instance.params[param.name] = '$IMAGE'
            hasSetImage = true
        } else if (param.type === ParamType.OBJECT && !hasSetAnnotation) {
            // 第一个标注参数默认使用数据集标注
            instance.params[param.name] = '$ANNOTATION'
            hasSetAnnotation = true
        } else {
            // 其他参数使用默认值
            instance.params[param.name] = param.default
        }
    })

    item.outputParams.forEach(param => {
        if (param.type === ParamType.IMAGE && !hasSetOutputImage) {
            instance.params.outputImageParam = param.name
            hasSetOutputImage = true
        } else if (param.type === ParamType.OBJECT && !hasSetOutputAnnotation) {
            instance.params.outputAnnotationParam = param.name
            hasSetOutputAnnotation = true
        }
    })

    selectedInstances.value.push(instance)
}

// 复制操作实例
const duplicateInstance = (instance: OperationInstance) => {
    const newInstance: OperationInstance = {
        ...instance,
        instanceId: nextInstanceId++,
        params: { ...instance.params },
    }
    selectedInstances.value.push(newInstance)
}

// 移除操作实例
const removeInstance = (index: number) => {
    selectedInstances.value.splice(index, 1)
}

// 配置实例参数
const configureInstance = (instance: OperationInstance) => {
    currentInstance.value = instance
    showConfigDialog.value = true
}

// 重置参数
const resetParams = () => {
    if (!currentInstance.value) return
    
    currentInstance.value.inputParams?.forEach(param => {
        paramValues.value[param.name] = param.default
    })
}

// 关闭对话框
const handleClose = () => {
    emit('update:modelValue', false)
}


// 修改预览图片的类型定义
interface PreviewImage {
  sourceImageUrl: string
  sourceImageId: number
  originalAnnotation: W3CAnnotation[]
  operations: {
    operationName: string
    operationType?: 'operation' | 'pipeline' | undefined
    processedImage: string
    processedAnnotation: W3CAnnotation[]
  }[]
}

// Modify generatePreview to group results by source image
const generatePreview = async () => {
    if (!canPreview.value) return

    try {
        previewLoading.value = true
        previewImages.value = []

        // Group preview results by source image
        const previewsByImage: Record<number, PreviewImage> = {}
        
        // Process up to 3 source images
        for (const img of props.sourceImages.slice(0, 3)) {
            // Get original annotation
            const annotationResponse = await annotationService.getImageAnnotation(img.id)
            const originalAnnotation = annotationResponse.annotations || []
            
            // Initialize preview entry for this image
            previewsByImage[img.id] = {
                sourceImageUrl: img.url,
                sourceImageId: img.id,
                originalAnnotation,
                operations: []
            }
            
            // Apply each operation to this image
            for (const instance of selectedInstances.value) {
                // Prepare instance parameters
                const params = await prepareInstanceParams(instance, {
                    ...img,
                    url: img.url,
                    annotation: originalAnnotation
                })
                
                // Apply the operation
                const result = instance.type === 'operation'
                    ? await cvOperationService.applyOperation(instance.id!, { inputParams: params })
                    : (await pipelineService.applyPipeline(instance.id!, { inputParams: params }))?.outputParams

                const { processedImage, processedAnnotation } = processResult(result, instance)
                // Add operation result to this image's preview
                previewsByImage[img.id].operations.push({
                    operationName: instance.name || (instance.type === 'operation' ? '操作' : '流水线'),
                    operationType: instance.type,
                    processedImage,
                    processedAnnotation: processedAnnotation || originalAnnotation
                })
            }
        }

        previewImages.value = Object.values(previewsByImage)
        console.log(previewImages.value)
    } catch (error) {
        console.error('生成预览失败:', error)
        $q.notify({
            type: 'negative',
            message: error instanceof Error ? error.message : t('generateData.notifications.previewError'),
            position: 'top'
        })
    } finally {
        previewLoading.value = false
    }
}


// Similarly modify the generateData function to apply operations in parallel
const generateData = async () => {
    if (!canGenerate.value) return

    try {
        generating.value = true
        showProgressDialog.value = true
        progressValue.value = 0
        progressText.value = t('common.loading')
        progressStatus.value = '正在准备数据...'

        // Prepare target dataset
        let targetDatasetId = await prepareTargetDataset()

        // Get all images to process
        const imagesToProcess = props.sourceImages
        let processedCount = 0
        const totalOperations = imagesToProcess.length * selectedInstances.value.length

        // For each image, apply each operation independently
        for (const img of imagesToProcess) {
            // Get original annotation if needed
            const annotationResponse = await annotationService.getImageAnnotation(img.id)
            const originalAnnotation = annotationResponse.annotations || []
            
            // Apply each operation independently to create new data
            for (const instance of selectedInstances.value) {
                // Prepare parameters using original image and annotation
                const params = await prepareInstanceParams(instance, {
                    ...img,
                    url: img.url,
                    annotation: originalAnnotation
                })
                
                // Apply the operation
                const result = instance.type === 'operation'
                    ? await cvOperationService.applyOperation(instance.id!, { inputParams: params })
                    : (await pipelineService.applyPipeline(instance.id!, { inputParams: params }))?.outputParams
                
                const { processedImage, processedAnnotation } = processResult(result, instance)
                
                // Convert base64 image to a File object
                const imageBlob = await fetch(`data:image/png;base64,${processedImage}`).then(r => r.blob())
                const imageFile = new File([imageBlob], `generated_${img.id}_${instance.id}.png`, { type: 'image/png' })
                
                // Upload the processed image to the target dataset
                const uploadedImages = await annotationService.uploadImages(targetDatasetId, [imageFile])
                
                // If upload successful, save the annotations to the new image
                if (uploadedImages && uploadedImages.length > 0) {
                    const newImageId = uploadedImages[0].id
                    
                    // Save the annotations to the new image
                    await annotationService.saveAnnotation(newImageId, {
                        annotations: processedAnnotation || originalAnnotation || []
                    })
                    
                    // Update progress
                    processedCount++
                    progressValue.value = processedCount / totalOperations
                    progressText.value = `已处理 ${processedCount} / ${totalOperations} 个操作`
                    progressStatus.value = `正在生成: ${instance.name || '操作'} (${processedCount}/${totalOperations})`
                }
            }
        }

        // Complete
        progressValue.value = 1
        progressStatus.value = t('generateData.notifications.generateSuccess')
        progressText.value = t('generateData.notifications.generateSuccess')
        
        emit('update:datasets')
        
        $q.notify({
            type: 'positive',
            message: t('generateData.notifications.generateSuccess'),
            position: 'top'
        })
    } catch (error) {
        console.error('生成数据失败:', error)
        progressStatus.value = t('generateData.notifications.generateError')
        progressText.value = error instanceof Error ? error.message : t('common.error')
        
        $q.notify({
            type: 'negative',
            message: t('generateData.notifications.generateError'),
            position: 'top'
        })
    } finally {
        generating.value = false
    }
}

// 准备目标数据集
const prepareTargetDataset = async () => {
    if (targetDatasetOption.value === 'new') {
        // 创建新数据集
        progressStatus.value = '正在创建目标数据集...'
        const newDataset = await annotationService.createDataset({
            name: newDatasetName.value,
            type: newDatasetType.value?.value
        })
        return newDataset.id
    } else if (targetDatasetOption.value === 'existing') {
        return selectedTargetDataset.value!.id
    } else {
        return props.sourceDataset.id
    }
}

// 取消生成
const cancelGeneration = async () => {
    try {
        // Set a flag to indicate cancelation request
        const willCancel = await new Promise<boolean>((resolve) => {
            $q.dialog({
                title: t('generateData.notifications.cancelConfirm.title'),
                message: t('generateData.notifications.cancelConfirm.message'),
                cancel: true,
                persistent: true
            }).onOk(() => resolve(true))
             .onCancel(() => resolve(false))
        })
        
        if (willCancel) {
            // Simply stop the process - no actual API call needed
            progressText.value = t('generateData.notifications.cancelConfirm.canceled')
            progressStatus.value = t('generateData.notifications.cancelConfirm.canceled')
            generating.value = false
            
            // Close the dialog after a delay
            setTimeout(() => {
                showProgressDialog.value = false
            }, 1000)
        }
    } catch (error) {
        console.error('取消生成失败:', error)
    }
}

// 关闭进度对话框
const closeProgressDialog = () => {
    showProgressDialog.value = false
}

// 监听对话框打开状态
watch(() => props.modelValue, (newVal) => {
    if (newVal) {
        // 对话框打开时加载数据
        loadData()
    }
})

// 组件挂载时初始化
onMounted(() => {
    if (props.modelValue) {
        loadData()
    }
})

// 添加辅助方法
const getParamsByType = (type: ParamType, direction: 'input' | 'output') => {
    if (!currentInstance.value) return []
    
    const params = direction === 'input' 
        ? currentInstance.value.inputParams 
        : currentInstance.value.outputParams
    
    return params?.filter(p => p.type === type) || []
}

// 检查是否为数据集图片参数
const isDatasetImageParam = (paramName: string): boolean => {
    const params = getParamsByType(ParamType.IMAGE, 'input')
    return params.some(p => p.name === paramName)
}

// 检查是否为数据集标注参数
const isDatasetAnnotationParam = (paramName: string): boolean => {
    const params = getParamsByType(ParamType.OBJECT, 'input')
    return params.some(p => p.name === paramName)
}

// 添加计算属性
const hasImageOutput = computed(() => {
    return getParamsByType(ParamType.IMAGE, 'output').length > 0
})

const hasObjectOutput = computed(() => {
    return getParamsByType(ParamType.OBJECT, 'output').length > 0
})

// 修改处理结果的部分
const processResult = (result: any, instance: OperationInstance) => {
    let processedImage = ''
    let processedAnnotation: W3CAnnotation[] | undefined = undefined
    
    // 使用选定的输出参数
    if (instance.params.outputImageParam) {
        processedImage = result[instance.params.outputImageParam]
    }
    
    if (instance.params.outputAnnotationParam) {
        // Handle different annotation formats
        const annotationResult = result[instance.params.outputAnnotationParam]
        if (Array.isArray(annotationResult)) {
            processedAnnotation = annotationResult
        } else if (typeof annotationResult === 'string') {
            try {
                // Try to parse string as JSON
                processedAnnotation = JSON.parse(annotationResult)
            } catch (e) {
                console.warn('Failed to parse annotation string:', e)
            }
        } else if (annotationResult && typeof annotationResult === 'object') {
            // Convert to array if it's a single object
            processedAnnotation = [annotationResult]
        }
    }
    
    return { processedImage, processedAnnotation }
}

// Modified prepareInstanceParams function to return only base64 data without data URL prefix
const prepareInstanceParams = async (instance: OperationInstance, sourceData: any) => {
    const params: Record<string, any> = {}
    
    // Process each input parameter
    for (const param of instance.inputParams || []) {
        const paramValue = instance.params[param.name]
        
        // Handle special parameter values
        if (paramValue === '$IMAGE' && param.type === ParamType.IMAGE) {
            // Convert image URL to base64 format
            try {
                let base64Data = ''
                
                // If URL is already a data URL, extract the base64 part
                if (sourceData.url.startsWith('data:')) {
                    base64Data = sourceData.url.split(',')[1] || sourceData.url
                } else {
                    // Fetch the image and convert to base64
                    const response = await fetch(sourceData.url)
                    const blob = await response.blob()
                    const reader = new FileReader()
                    const dataUrl = await new Promise<string>((resolve) => {
                        reader.onload = (e) => resolve(e.target?.result as string)
                        reader.readAsDataURL(blob)
                    })
                    
                    // Extract the base64 part from the data URL
                    base64Data = dataUrl.split(',')[1] || dataUrl
                }
                
                params[param.name] = base64Data
            } catch (error) {
                console.error('Failed to convert image to base64:', error)
                // Fallback to using the URL directly
                params[param.name] = sourceData.url
            }
        } 
        else if (paramValue === '$ANNOTATION' && param.type === ParamType.OBJECT) {
            // Use the source annotation data
            params[param.name] = sourceData.annotation || []
        }
        else if (paramValue === 'custom' && param.type === ParamType.IMAGE) {
            // Handle custom uploaded image
            const file = instance.params[`${param.name}_file`]
            if (file) {
                // Convert file to data URL and extract just the base64 part
                const reader = new FileReader()
                const dataUrl = await new Promise<string>((resolve) => {
                    reader.onload = (e) => resolve(e.target?.result as string)
                    reader.readAsDataURL(file)
                })
                
                // Extract the base64 part from the data URL
                const base64Data = dataUrl.split(',')[1] || dataUrl
                params[param.name] = base64Data
            }
        }
        else if (paramValue === 'custom' && param.type === ParamType.OBJECT) {
            // Handle custom object data (like annotations)
            const customData = instance.params[`${param.name}_data`]
            try {
                params[param.name] = typeof customData === 'string' ? 
                    JSON.parse(customData) : customData
            } catch (e) {
                params[param.name] = customData
            }
        }
        else {
            // Use the parameter value as is
            params[param.name] = paramValue
        }
    }
    
    return params
}
</script>

<style lang="scss" scoped>
.generate-data-dialog {
    .generate-data-card {
        display: flex;
        flex-direction: column;
        height: 100vh;
        max-height: 100vh;
        margin: 0;
        background: var(--dark-page);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);

        // 专业的点阵背景图案
        background-image:
            radial-gradient(rgba(0, 0, 0, 0.3) 15%, transparent 16%),
            radial-gradient(rgba(0, 0, 0, 0.3) 15%, transparent 16%);
        background-size: 12px 12px;
        background-position: 0 0, 6px 6px;
        background-color: var(--dark-page);
    }

    .preview-container {
        height: 60vh;
        overflow-y: auto;
        border: 1px solid var(--q-dark-separator);
        border-radius: 4px;
        padding: 12px;
        background: var(--dark-card);

        // Industrial-style scrollbar
        &::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        &::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.1);
            border-radius: 4px;
        }
        
        &::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            
            &:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        }
    }

    .preview-images {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        padding: 8px;
    }

    .preview-pipeline {
        margin-bottom: 32px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        overflow: hidden;
    }

    .pipeline-header {
        padding: 8px 12px;
        background: rgba(0, 0, 0, 0.2);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .image-info {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.8);
    }

    .source-image-row {
        padding: 16px 16px 0 16px;
    }

    .source-image-container {
        width: 100%;
        background: rgba(20, 20, 20, 0.7);
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        overflow: hidden;
    }

    .stage-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 10px;
        background: linear-gradient(to bottom, rgba(60, 60, 60, 0.8), rgba(40, 40, 40, 0.8));
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }

    .stage-name {
        font-size: 12px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.9);
    }

    .stage-type {
        font-size: 10px;
        padding: 2px 4px;
    }

    .stage-content {
        padding: 8px;
    }

    .stage-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 8px;
        height: 24px;
    }

    .annotation-container {
        position: relative;
        width: 100%;
        height: 160px;
        background: #000;
        overflow: hidden;
        border-radius: 2px;
        
        &::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5);
            pointer-events: none;
        }
    }

    .preview-image {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }

    .annotation-layer {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
        
        :deep(svg) {
            width: 100%;
            height: 100%;
        }
        
        :deep(.annotation-box) {
            fill: rgba(0, 120, 255, 0.15);
            stroke: rgb(0, 120, 255);
            stroke-width: 1.5px;
            vector-effect: non-scaling-stroke;
        }
        
        :deep(.annotation-polygon) {
            fill: rgba(0, 180, 120, 0.15);
            stroke: rgb(0, 180, 120);
            stroke-width: 1.5px;
            vector-effect: non-scaling-stroke;
        }
        
        :deep(.annotation-text) {
            fill: white;
            font-size: 10px;
            font-weight: bold;
            text-shadow: 0 0 3px black;
        }
    }

    .no-preview-message {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 300px;
        background: var(--dark-card-header);
        border-radius: 4px;
    }

    .operations-section {
        max-height: calc(100vh - 200px);
        overflow-y: auto;
    }

    .available-operations {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding: 8px;
        border-radius: 4px;
        background: rgba(0, 0, 0, 0.1);
    }

    .operation-chip {
        background: var(--dark-card);
        color: #fff;
        transition: all 0.3s ease;

        &:hover {
            background: var(--industrial-blue-50);
            transform: translateY(-1px);
        }

        :deep(.q-badge) {
            font-size: 10px;
            padding: 2px 4px;
        }
    }

    .operation-results {
        display: flex;
        flex-wrap: wrap;
        padding: 16px;
        gap: 16px;
    }

    .operation-result {
        flex: 1;
        min-width: 200px;
        max-width: calc(33.33% - 11px);
        background: rgba(30, 30, 30, 0.7);
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        overflow: hidden;
    }

    .operation-header {
        display: flex;
        align-items: center;
        padding: 6px 10px;
        background: linear-gradient(to bottom, rgba(60, 60, 60, 0.8), rgba(40, 40, 40, 0.8));
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .operation-title {
        font-size: 12px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.9);
        margin-right: 8px;
    }

    .operation-content {
        padding: 8px;
    }

    .image-info {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.6);
    }

    /* Responsive adjustments */
    @media (max-width: 1200px) {
        .operation-result {
            max-width: calc(50% - 8px);
        }
    }

    @media (max-width: 768px) {
        .operation-result {
            max-width: 100%;
        }
    }
}
</style>