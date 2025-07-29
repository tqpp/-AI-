<template>
    <q-dialog @keydown.esc="handleClose" :model-value="modelValue" @update:model-value="emit('update:modelValue', $event)" maximized persistent
        transition-show="slide-up" transition-hide="slide-down">
        <q-card class="editor-dialog">
            <q-card-section class="editor-header row items-center q-py-sm">
                <div class="row items-center">
                    <q-icon name="code" size="24px" color="info" class="q-mr-sm" />
                    <div class="text-h6">{{ operation.id ? t('cv.operationEditor.title.edit') : t('cv.operationEditor.title.new') }}</div>
                </div>
                <q-space />
                <q-btn-group flat>
                    <q-btn color="secondary" icon="science" :label="t('cv.operationEditor.actions.test')" @click="showTestPanel = true" />
                    <q-btn :loading="saving" color="primary" icon="save" :label="t('cv.operationEditor.actions.save')" @click="handleSubmit" />
                    <q-btn flat icon="close" @click="handleClose">
                        <q-tooltip>{{ t('cv.operationEditor.actions.close') }}</q-tooltip>
                    </q-btn>
                </q-btn-group>
            </q-card-section>

            <!-- 原有的editor-section内容 -->
            <q-card-section class="editor-section">
                <div class="row no-wrap">
                    <!-- 左侧表单面板 -->
                    <div class="col-auto form-panel">
                        <div class="form-container">
                            <!-- 基本信息卡片 -->
                            <q-expansion-item default-opened icon="info" :label="t('cv.operationEditor.basicInfo.title')" header-class="text-primary">
                                <q-card flat bordered>
                                    <q-card-section>
                                        <q-input v-model="localOperation.name" :label="t('cv.operationEditor.basicInfo.name')"
                                            :rules="[val => !!val || t('cv.operationEditor.basicInfo.nameRequired')]" class="q-mb-md" outlined dense>
                                            <template v-slot:prepend>
                                                <q-icon name="label" />
                                            </template>
                                        </q-input>

                                        <q-input v-model="localOperation.description" :label="t('cv.operationEditor.basicInfo.description')" type="textarea"
                                            class="q-mb-md" outlined dense autogrow>
                                            <template v-slot:prepend>
                                                <q-icon name="description" />
                                            </template>
                                        </q-input>
                                    </q-card-section>
                                </q-card>
                            </q-expansion-item>

                            <!-- 参数配置部分 -->
                            <q-expansion-item default-opened icon="settings" :label="t('cv.operationEditor.parameters.title')" header-class="text-primary">
                                <q-card flat bordered>
                                    <q-tabs v-model="activeParamTab" dense class="text-grey" active-class="text-primary"
                                        indicator-color="primary" align="justify" narrow-indicator>
                                        <q-tab name="input" icon="input" :label="t('cv.operationEditor.parameters.tabs.input')" />
                                        <q-tab name="output" icon="output" :label="t('cv.operationEditor.parameters.tabs.output')" />
                                    </q-tabs>

                                    <q-separator />

                                    <q-tab-panels v-model="activeParamTab" animated>
                                        <!-- 输入参数面板 -->
                                        <q-tab-panel name="input" class="q-pa-none">
                                            <div class="params-panel">
                                                <div class="params-list">
                                                    <q-list separator>
                                                        <q-item v-for="(param, index) in localOperation.inputParams || []"
                                                            :key="index">
                                                            <div class="row full-width q-col-gutter-sm">
                                                                <div class="col-12">
                                                                    <div class="row items-center justify-between">
                                                                        <div class="text-subtitle2">{{ t('cv.operationEditor.parameters.param', { index: index + 1 }) }}
                                                                        </div>
                                                                        <q-btn flat round dense color="negative"
                                                                            icon="delete"
                                                                            @click="removeInputParam(index)" />
                                                                    </div>
                                                                </div>
                                                                <ParameterInput :param="param"
                                                                    :paramTypeOptions="paramTypeOptions" />
                                                            </div>
                                                        </q-item>
                                                    </q-list>
                                                </div>
                                                <q-btn flat class="full-width q-mt-sm" icon="add" :label="t('cv.operationEditor.parameters.addInput')"
                                                    @click="addInputParam" />
                                            </div>
                                        </q-tab-panel>

                                        <!-- 输出参数面板 -->
                                        <q-tab-panel name="output" class="q-pa-none">
                                            <div class="params-panel">
                                                <div class="params-list">
                                                    <q-list separator>
                                                        <q-item v-for="(param, index) in localOperation.outputParams || []"
                                                            :key="index">
                                                            <div class="row full-width q-col-gutter-sm">
                                                                <div class="col-12">
                                                                    <div class="row items-center justify-between">
                                                                        <div class="text-subtitle2">{{ t('cv.operationEditor.parameters.param', { index: index + 1 }) }}
                                                                        </div>
                                                                        <q-btn flat round dense color="negative"
                                                                            icon="delete"
                                                                            @click="removeOutputParam(index)" />
                                                                    </div>
                                                                </div>
                                                                <ParameterInput :param="param"
                                                                    :paramTypeOptions="paramTypeOptions" />
                                                            </div>
                                                        </q-item>
                                                    </q-list>
                                                </div>
                                                <q-btn flat class="full-width q-mt-sm" icon="add" :label="t('cv.operationEditor.parameters.addOutput')"
                                                    @click="addOutputParam" />
                                            </div>
                                        </q-tab-panel>
                                    </q-tab-panels>
                                </q-card>
                            </q-expansion-item>
                        </div>
                    </div>

                    <!-- 右侧代码编辑器 -->
                    <div class="col code-panel">
                        <q-card flat bordered class="code-editor-card">
                            <q-card-section class="code-editor-header">
                                <div class="text-subtitle2">{{ t('cv.operationEditor.codeEditor.title') }}</div>
                            </q-card-section>
                            <q-separator />
                            <div id="monaco-editor" class="editor-container" />
                        </q-card>
                    </div>
                </div>
            </q-card-section>

            <!-- 添加测试面板组件 -->
            <operation-test-panel
                v-model="showTestPanel"
                :operation="operation"
            />
        </q-card>
    </q-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { debounce } from 'lodash'
import * as monaco from 'monaco-editor'
import { useI18n } from 'vue-i18n'
import { CVOperation, ParamType } from '@/services/cv_operation'
import ParameterInput from './ParameterInput.vue'
import { toRaw } from 'vue'
import OperationTestPanel from './OperationTestPanel.vue'

const { t } = useI18n()

const props = defineProps<{
    modelValue: boolean
    operation: CVOperation
    saving: boolean
}>()

const emit = defineEmits<{
    'update:modelValue': [value: boolean]
    'submit': [operation: Partial<CVOperation>]
    'update:operation': [operation: Partial<CVOperation>]
}>()

const paramTypeOptions = Object.values(ParamType).map(type => {
    const iconMap: Record<ParamType, string> = {
        [ParamType.TEXT]: 'text_fields',
        [ParamType.NUMBER]: 'numbers',
        [ParamType.BOOLEAN]: 'toggle_on',
        [ParamType.IMAGE]: 'image',
        [ParamType.ARRAY]: 'view_list',
        [ParamType.OBJECT]: 'data_object'
    }
    return {
        label: type,
        value: type,
        icon: iconMap[type]
    }
})

// 编辑器状态管理
const editor = ref<any>(null)
let disposeEditor: (() => void) | null = null
const editorReady = ref(false)
const activeParamTab = ref('input')

// 创建一个本地操作数据的副本
const localOperation = ref<Partial<CVOperation>>({
    ...props.operation,
    inputParams: [...(props.operation.inputParams || [])],
    outputParams: [...(props.operation.outputParams || [])]
})

// 监听props变化，更新本地数据
watch(() => props.operation, (newOperation) => {
    localOperation.value = {
        ...newOperation,
        inputParams: [...(newOperation.inputParams || [])],
        outputParams: [...(newOperation.outputParams || [])]
    }
}, { deep: true })

// 更新本地数据并触发父组件更新
const updateOperation = (updates: Partial<CVOperation>) => {
    localOperation.value = {
        ...localOperation.value,
        ...updates
    }
    emit('update:operation', localOperation.value)
}

// 代码模板管理
const generateTemplate = () => {
  const inputParams = (props.operation.inputParams || []).map(p => p.name).join(', ')
  return `def process(${inputParams}):
    return {}`
}

// 防抖处理代码更新
const updateEditorValue = debounce((newValue: string) => {
  if (editor.value && editorReady.value) {
    const position = toRaw(editor.value).getPosition()
    toRaw(editor.value).setValue(newValue)
    toRaw(editor.value).setPosition(position)
  }
}, 300)

// Add readonly line handling
const readOnlyLines = new Set<number>()

// 初始化编辑器
const initEditor = async () => {
  await nextTick()
  const container = document.getElementById('monaco-editor')
  if (!container) return

  try {
    // 清理旧的编辑器实例
    if (editor.value) {
      disposeEditor?.()
    }

    monaco.languages.register({ id: 'python' })
    const initialCode = props.operation.code || generateTemplate()
    editor.value = monaco.editor.create(container, {
      value: initialCode,
      language: 'python',
      theme: 'vs-dark',
      automaticLayout: true,
      minimap: { enabled: false },
      readOnly: false,
      wordWrap: 'on',
      scrollBeyondLastLine: false,
      fontSize: 14,
      tabSize: 4,
      renderWhitespace: 'selection',
      quickSuggestions: true,
      rulers: [80],
      formatOnPaste: true,
      formatOnType: true
    })

    // 只标记第一行def为只读
    const lines = initialCode.split('\n')
    const decorations: monaco.editor.IModelDeltaDecoration[] = []
    
    // 找到def process行并标记为只读
    const processLineIndex = lines.findIndex(line => line.trim().startsWith('def process('))
    if (processLineIndex !== -1) {
      readOnlyLines.clear() // 清除之前的只读行
      readOnlyLines.add(processLineIndex + 1) // 添加def行为只读
      decorations.push({
        range: new monaco.Range(processLineIndex + 1, 1, processLineIndex + 1, 1000),
        options: {
          isWholeLine: true,
          inlineClassName: 'readonly-line',
          className: 'readonly-line'
        }
      })
    }

    // 添加编辑预防
    toRaw(editor.value).onDidChangeCursorPosition((e: monaco.editor.ICursorPositionChangedEvent) => {
      if (readOnlyLines.has(e.position.lineNumber)) {
        const model = toRaw(editor.value).getModel()
        if (model) {
          const lastLine = model.getLineCount()
          toRaw(editor.value).setPosition({ lineNumber: Math.min(e.position.lineNumber + 1, lastLine), column: 1 })
        }
      }
    })

    toRaw(editor.value).onKeyDown((e: monaco.IKeyboardEvent) => {
      const position = toRaw(editor.value).getPosition()
      if (position && readOnlyLines.has(position.lineNumber)) {
        e.preventDefault()
      }
    })

    editorReady.value = true

    disposeEditor = () => {
      if (editor.value) {
        toRaw(editor.value).dispose()
        editor.value = null
      }
      editorReady.value = false
    }
  } catch (error) {
    console.error('初始化编辑器失败:', error)
  }
}

// 监听对话框显示状态
watch(() => props.modelValue, async (newVal) => {
  if (newVal) {
    await initEditor()
  } else {
    disposeEditor?.()
  }
})

// 清理资源
onBeforeUnmount(() => {
  disposeEditor?.()
  updateEditorValue.cancel()
})

// 工具函数
const extractUserCode = (code: string) => {
  try {
    // 按行分割代码
    const lines = code.split('\n')
    
    // 找到def process行
    const processLineIndex = lines.findIndex(line => line.trim().startsWith('def process('))
    if (processLineIndex === -1) return ''

    // 提取def process后面的所有代码
    const userCode = lines.slice(processLineIndex + 1)
      .join('\n')

    return userCode
  } catch (error) {
    console.error('提取用户代码失败:', error)
    return ''
  }
}

const generateTemplateWithUserCode = (userCode: string) => {
  const inputParams = props.operation.inputParams?.map(p => p.name).join(', ') || ''
  return `def process(${inputParams}):
${userCode}`
}

// Methods
const addInputParam = () => {
    if (!localOperation.value.inputParams) {
        localOperation.value.inputParams = []
    }
    const idx = localOperation.value.inputParams.length + 1
    const newParam = {
        name: `input_${idx}`,
        type: ParamType.TEXT,
        description: '',
        default: undefined,
        required: false
    }
    localOperation.value.inputParams.push(newParam)
    updateOperation({ inputParams: localOperation.value.inputParams })
}

const addOutputParam = () => {
    if (!localOperation.value.outputParams) {
        localOperation.value.outputParams = []
    }
    const idx = localOperation.value.outputParams.length + 1
    const newParam = {
        name: `output_${idx}`,
        type: ParamType.TEXT,
        description: '',
        default: undefined,
        required: false
    }
    localOperation.value.outputParams.push(newParam)
    updateOperation({ outputParams: localOperation.value.outputParams })
}

const removeInputParam = (index: number) => {
    if (!localOperation.value.inputParams) return
    localOperation.value.inputParams.splice(index, 1)
    updateOperation({ inputParams: localOperation.value.inputParams })
}

const removeOutputParam = (index: number) => {
    if (!localOperation.value.outputParams) return
    localOperation.value.outputParams.splice(index, 1)
    updateOperation({ outputParams: localOperation.value.outputParams })
}

const handleClose = () => {
    emit('update:modelValue', false)
    // 重置表单
    resetForm()
}

// 添加重置表单方法
const resetForm = () => {
  localOperation.value = {
    name: '',
    description: '',
    code: `def process():
    return {}`,
    inputParams: [],
    outputParams: []
  }
  activeParamTab.value = 'input'
}

// 生命周期钩子
onMounted(() => {
    initEditor()
})

// 监听编辑操作变化
watch(() => props.operation.code, (newCode) => {
    if (editor.value && editorReady.value && newCode !== toRaw(editor.value).getValue()) {
        toRaw(editor.value).setValue(newCode || '')
    }
}, { immediate: true })

// Editor value management
const getEditorValue = () => {
  try {
    if (!editor.value || !editorReady.value) return ''
    return toRaw(editor.value).getValue() || ''
  } catch (error) {
    console.error('获取编辑器内容失败:', error)
    return ''
  }
}

const setEditorValue = debounce((value: string) => {
  try {
    if (!editor.value || !editorReady.value) return
    const editorInstance = toRaw(editor.value)
    const position = editorInstance.getPosition()
    editorInstance.setValue(value)
    if (position) {
      editorInstance.setPosition(position)
    }
  } catch (error) {
    console.error('设置编辑器内容失败:', error)
  }
}, 300)

// 修改监听参数变化的处理
watch([() => localOperation.value.inputParams, () => localOperation.value.outputParams], () => {
    if (!editorReady.value) return
    
    try {
        const currentCode = getEditorValue()
        const userCode = extractUserCode(currentCode)
        const newTemplate = generateTemplateWithUserCode(userCode)
        setEditorValue(newTemplate)
    } catch (error) {
        console.error('更新代码模板失败:', error)
    }
}, { deep: true })

// 修改提交处理
const handleSubmit = () => {
    const operationData = {
        ...localOperation.value,
        code: getEditorValue()
    }
    emit('submit', operationData)
}

// 添加测试面板组件
const showTestPanel = ref(false)
</script>

<style lang="scss" scoped>
.editor-dialog {
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

    // 专业化的头部样式
    .editor-header {
        flex: 0 0 auto;
        background: linear-gradient(180deg, var(--dark-card) 0%, var(--dark-card-header) 100%);
        border-bottom: 1px solid var(--border-color);
        padding: 8px 16px;

        .text-h6 {
            font-weight: 500;
            letter-spacing: 0.5px;
            color: var(--text-primary);
        }

        .q-icon {
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
        }

        .q-btn-group {
            border: 1px solid var(--border-color);
            border-radius: 4px;
            overflow: hidden;

            .q-btn {
                border: none;
                background: transparent;
                
                &:hover {
                    background: rgba(255, 255, 255, 0.1);
                }

                &:active {
                    background: rgba(0, 0, 0, 0.2);
                }
            }
        }
    }

    .editor-section {
        flex: 1;
        min-height: 0;
        display: flex;
        
        .row {
            flex: 1;
            min-height: 0;
            margin: 0;
            
            // 左侧面板样式增强
            .form-panel {
                width: 400px;
                min-width: 400px;
                border-right: 1px solid var(--border-color);
                background: var(--dark-card);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 2px 0 8px rgba(0, 0, 0, 0.2);

                .form-container {
                    flex: 1;
                    padding: 16px;
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                    overflow-y: auto;

                    // 自定义滚动条
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
            }

            // 右侧代码编辑器面板样式
            .code-panel {
                flex: 1;
                display: flex;
                flex-direction: column;
                min-height: 0;
                
                .code-editor-card {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    margin: 16px;
                    border: 1px solid var(--border-color);
                    border-radius: 4px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                    
                    .code-editor-header {
                        background: linear-gradient(180deg, var(--dark-card) 0%, var(--dark-card-header) 100%);
                        padding: 8px 16px;
                        border-bottom: 1px solid var(--border-color);

                        .text-subtitle2 {
                            font-weight: 500;
                            color: var(--text-primary);
                        }
                    }
                    
                    .editor-container {
                        flex: 1;
                        min-height: 0;
                    }
                }
            }
        }
    }

    // 参数面板样式增强
    .params-panel {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 0;
        padding: 16px;

        .params-list {
            flex: 1;
            overflow-y: auto;
            background: var(--dark-card-header);
            border-radius: 4px;
            padding: 8px;
            border: 1px solid var(--border-color);
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);

            .q-list {
                >.q-item {
                    background: var(--dark-card);
                    border-radius: 4px;
                    margin-bottom: 8px;
                    transition: all 0.3s ease;
                    border: 1px solid var(--border-color);
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

                    &:hover {
                        border-color: var(--primary);
                        background: linear-gradient(
                            180deg,
                            var(--dark-card) 0%,
                            rgba(25, 118, 210, 0.1) 100%
                        );
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                    }

                    &:last-child {
                        margin-bottom: 0;
                    }
                }
            }
        }

        .q-btn.full-width {
            margin-top: 16px;
            border: 1px solid var(--border-color);
            background: linear-gradient(180deg, var(--dark-card) 0%, var(--dark-card-header) 100%);

            &:hover {
                background: linear-gradient(180deg, var(--dark-card-header) 0%, var(--dark-card) 100%);
            }
        }
    }
}

// 扩展面板样式增强
.q-expansion-item {
    :deep(.q-expansion-item__container) {
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 8px;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

        .q-expansion-item__header {
            padding: 8px 16px;
            background: linear-gradient(180deg, var(--dark-card) 0%, var(--dark-card-header) 100%);
        }
    }
}

// 选项卡样式增强
.q-tabs {
    background: linear-gradient(180deg, var(--dark-card) 0%, var(--dark-card-header) 100%);
    border-bottom: 1px solid var(--border-color);
}

// 只读行样式增强
.readonly-line {
    background: linear-gradient(90deg, 
        rgba(128, 128, 128, 0.2) 0%,
        rgba(128, 128, 128, 0.1) 100%
    );
    cursor: not-allowed !important;
    border-left: 2px solid var(--primary);
}

.readonly-line:hover {
    background: linear-gradient(90deg,
        rgba(128, 128, 128, 0.3) 0%,
        rgba(128, 128, 128, 0.2) 100%
    );
}
</style>