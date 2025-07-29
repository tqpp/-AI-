<template>
  <q-dialog @keydown.esc="handleClose" :model-value="modelValue" @update:model-value="emit('update:modelValue', $event)"
    maximized persistent transition-show="slide-up" transition-hide="slide-down">
    <q-card class="editor-dialog">
      <q-card-section class="editor-header row items-center q-py-sm">
        <div class="row items-center">
          <q-icon name="account_tree" size="24px" color="info" class="q-mr-sm" />
          <div class="text-h6">{{ pipeline.id ? '编辑流水线' : '新建流水线' }}</div>
        </div>
        <q-space />
        <q-btn-group flat>
          <q-btn color="secondary" icon="science" label="运行" @click="showTestPanel = true" />
          <q-btn :loading="saving" color="primary" icon="save" label="保存" @click="handleSubmit" />
          <q-btn flat icon="close" @click="handleClose">
            <q-tooltip>关闭</q-tooltip>
          </q-btn>
        </q-btn-group>
      </q-card-section>

      <q-card-section class="editor-section">
        <div class="row no-wrap">
          <!-- 左侧表单面板 -->
          <div class="col-auto form-panel">
            <div class="form-container">
              <!-- 基本信息卡片 -->
              <q-expansion-item default-opened icon="info" label="基本信息" header-class="text-primary">
                <q-card flat bordered>
                  <q-card-section>
                    <q-input v-model="localPipeline.name" label="流水线名称" :rules="[val => !!val || '请输入流水线名称']"
                      class="q-mb-md" outlined dense>
                      <template v-slot:prepend>
                        <q-icon name="label" />
                      </template>
                    </q-input>

                    <q-input v-model="localPipeline.description" label="描述" type="textarea" class="q-mb-md" outlined
                      dense autogrow>
                      <template v-slot:prepend>
                        <q-icon name="description" />
                      </template>
                    </q-input>
                  </q-card-section>
                </q-card>
              </q-expansion-item>

              <!-- 节点工具箱 -->
              <q-expansion-item default-opened icon="widgets" label="节点工具箱" header-class="text-primary">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="row q-col-gutter-sm">
                      <div class="col-6" v-for="(nodeType, index) in availableNodeTypes" :key="index">
                        <q-card flat bordered class="node-tool" @mousedown="startDrag(nodeType)">
                          <q-card-section class="q-pa-sm">
                            <div class="row items-center no-wrap">
                              <q-icon :name="getNodeIcon(nodeType)" size="24px" class="q-mr-sm" />
                              <div class="text-subtitle2">{{ getNodeLabel(nodeType) }}</div>
                            </div>
                          </q-card-section>
                        </q-card>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>

              <!-- 节点属性编辑器 -->
              <q-expansion-item v-if="selectedNode" default-opened icon="tune" label="节点属性" header-class="text-primary">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="row q-col-gutter-md">
                      <!-- For START nodes, show pipeline input parameters -->
                      <template v-if="selectedNode.type === NodeType.START">
                        <div class="col-12">
                          <div class="text-subtitle1 q-mb-md">
                            <q-icon name="input" class="q-mr-sm" />
                            输入参数配置
                          </div>
                        </div>

                        <!-- Input parameters list -->
                        <div class="col-12">
                          <div class="params-panel">
                            <div class="params-list">
                              <q-list separator>
                                <q-item v-for="(param, index) in localPipeline.inputParams || []" :key="index">
                                  <div class="row full-width q-col-gutter-sm">
                                    <div class="col-12">
                                      <div class="row items-center justify-between">
                                        <div class="text-subtitle2">参数 {{ index + 1 }}</div>
                                        <q-btn flat round dense color="negative" icon="delete"
                                          @click="removeInputParam(index)" />
                                      </div>
                                    </div>
                                    <ParameterInput :param="param" :paramTypeOptions="paramTypeOptions" />
                                  </div>
                                </q-item>
                              </q-list>
                            </div>
                            <q-btn flat class="full-width q-mt-sm" icon="add" label="添加输入参数" @click="addInputParam" />
                          </div>
                        </div>
                      </template>

                      <!-- For END nodes, show pipeline output parameters -->
                      <template v-else-if="selectedNode.type === NodeType.END">
                        <div class="col-12">
                          <div class="text-subtitle1 q-mb-md">
                            <q-icon name="output" class="q-mr-sm" />
                            输出参数配置
                          </div>
                        </div>

                        <!-- Output parameters list -->
                        <div class="col-12">
                          <div class="params-panel">
                            <div class="params-list">
                              <q-list separator>
                                <q-item v-for="(param, index) in localPipeline.outputParams || []" :key="index">
                                  <div class="row full-width q-col-gutter-sm">
                                    <div class="col-12">
                                      <div class="row items-center justify-between">
                                        <div class="text-subtitle2">参数 {{ index + 1 }}</div>
                                        <q-btn flat round dense color="negative" icon="delete"
                                          @click="removeOutputParam(index)" />
                                      </div>
                                    </div>
                                    <ParameterInput :param="param" :paramTypeOptions="paramTypeOptions" />
                                    
                                    <!-- Add source mapping for output parameters -->
                                    <div class="col-12 q-mt-sm">
                                      <q-select
                                        :model-value="getEndNodeOutputMapping(param.name)"
                                        :options="getEndNodeOutputOptions().filter(opt => opt.type === param.type)"
                                        label="映射到节点输出"
                                        outlined
                                        dense
                                        emit-value
                                        map-options
                                        clearable
                                        @update:model-value="value => updateEndNodeOutputMapping(param.name, value)">
                                        <template v-slot:prepend>
                                          <q-icon name="link" />
                                        </template>
                                        <template v-slot:no-option>
                                          <q-item>
                                            <q-item-section class="text-grey">
                                              没有找到匹配类型的节点输出
                                            </q-item-section>
                                          </q-item>
                                        </template>
                                      </q-select>
                                    </div>
                                  </div>
                                </q-item>
                              </q-list>
                            </div>
                            <q-btn flat class="full-width q-mt-sm" icon="add" label="添加输出参数" @click="addOutputParam" />
                          </div>
                        </div>
                      </template>

                      <!-- For other nodes (not START or END), show regular properties -->
                      <template v-else>
                        <div class="col-12">
                          <q-input v-model="selectedNode.name" label="节点名称" outlined dense>
                            <template v-slot:prepend>
                              <q-icon name="title" />
                            </template>
                          </q-input>
                        </div>

                        <!-- 操作节点特有属性 -->
                        <template v-if="selectedNode.type === NodeType.OPERATION">
                          <div class="col-12">
                            <q-select v-model="selectedNode.operationId" :options="operations" option-value="id"
                              option-label="name" label="选择操作" outlined dense emit-value map-options use-input
                              input-debounce="300" @filter="filterOperations"
                              @update:model-value="handleOperationChange">
                              <template v-slot:prepend>
                                <q-icon name="code" />
                              </template>
                              <template v-slot:no-option>
                                <q-item>
                                  <q-item-section class="text-grey">
                                    没有找到匹配的操作
                                  </q-item-section>
                                </q-item>
                              </template>
                              <template v-slot:option="scope">
                                <q-item v-bind="scope.itemProps">
                                  <q-item-section>
                                    <q-item-label>{{ scope.opt.name }}</q-item-label>
                                    <q-item-label caption>{{ scope.opt.description || '无描述' }}</q-item-label>
                                  </q-item-section>
                                </q-item>
                              </template>
                            </q-select>
                          </div>

                          <!-- 操作参数配置 -->
                          <div v-if="selectedOperation" class="col-12 q-mt-md">
                            <div class="text-subtitle1 q-mb-sm">
                              <q-icon name="settings" class="q-mr-xs" />
                              参数配置
                              <q-spinner v-if="loadingOperation" size="1em" class="q-ml-xs" />
                            </div>
                            <q-card flat bordered class="operation-params">
                              <q-list separator>
                                <q-item v-for="param in selectedOperation.inputParams" :key="param.name">
                                  <q-item-section>
                                    <div class="row q-col-gutter-sm">
                                      <div class="col-12">
                                        <div class="row items-center">
                                          <div class="text-subtitle2">{{ param.name }}</div>
                                          <q-space />
                                          <q-chip dense size="sm" :color="getTypeColor(param.type)">
                                            {{ param.type }}
                                          </q-chip>
                                        </div>
                                        <q-item-label caption>{{ param.description || '无描述' }}</q-item-label>
                                      </div>

                                      <div class="col-12">
                                        <!-- 参数值来源选择 -->
                                        <q-select :model-value="getParamConfigValue(selectedNode, param.name, 'source')"
                                          :options="getParamSourceOptions(param)" label="值来源" outlined dense emit-value
                                          map-options
                                          @update:model-value="value => updateNodeParamConfig(param.name, 'source', value)">
                                          <template v-slot:prepend>
                                            <q-icon name="link" />
                                          </template>
                                        </q-select>
                                      </div>

                                      <!-- 如果是自定义值，则显示值编辑器 -->
                                      <div v-if="getParamConfigValue(selectedNode, param.name, 'source') === 'custom'"
                                        class="col-12">
                                        <template v-if="param.type === ParamType.TEXT">
                                          <q-input :model-value="getParamConfigValue(selectedNode, param.name, 'value')"
                                            label="自定义值" outlined dense
                                            @update:model-value="value => updateNodeParamConfig(param.name, 'value', value)">
                                          </q-input>
                                        </template>

                                        <template v-else-if="param.type === ParamType.NUMBER">
                                          <q-input :model-value="getParamConfigValue(selectedNode, param.name, 'value')"
                                            type="number" label="自定义值" outlined dense
                                            @update:model-value="value => updateNodeParamConfig(param.name, 'value', value)">
                                          </q-input>
                                        </template>

                                        <template v-else-if="param.type === ParamType.BOOLEAN">
                                          <q-toggle
                                            :model-value="getParamConfigValue(selectedNode, param.name, 'value')"
                                            label="自定义值"
                                            @update:model-value="value => updateNodeParamConfig(param.name, 'value', value)">
                                          </q-toggle>
                                        </template>

                                        <template v-else>
                                          <q-input :model-value="getParamConfigValue(selectedNode, param.name, 'value')"
                                            type="textarea" label="自定义值 (JSON格式)" outlined dense
                                            @update:model-value="value => updateNodeParamConfig(param.name, 'value', value)">
                                          </q-input>
                                        </template>
                                      </div>
                                    </div>
                                  </q-item-section>
                                </q-item>
                              </q-list>
                            </q-card>
                          </div>
                        </template>

                        <!-- 条件节点特有属性 -->
                        <template v-if="selectedNode.type === NodeType.CONDITION">
                          <div class="col-12">
                            <q-input v-model="selectedNode.config!.condition" label="条件表达式" outlined dense
                              hint="使用JavaScript表达式，例如: input.value > 10">
                              <template v-slot:prepend>
                                <q-icon name="code" />
                              </template>
                            </q-input>
                          </div>
                        </template>
                      </template>
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>
            </div>
          </div>

          <!-- 右侧流水线画布 -->
          <div class="col flow-panel">
            <q-card flat bordered class="flow-editor-card">
              <q-card-section class="flow-editor-header">
                <div class="text-subtitle2">流水线设计器</div>
                <q-space />
                <q-btn-group flat>
                  <q-btn flat dense icon="undo" @click="undo" :disable="!canUndo">
                    <q-tooltip>撤销 (Ctrl+Z)</q-tooltip>
                  </q-btn>
                  <q-btn flat dense icon="redo" @click="redo" :disable="!canRedo">
                    <q-tooltip>重做 (Ctrl+Y)</q-tooltip>
                  </q-btn>
                  <q-separator vertical inset />
                  <q-btn flat dense icon="delete" @click="deleteSelected" :disable="!selectedNode && !selectedEdge">
                    <q-tooltip>删除选中元素 (Delete)</q-tooltip>
                  </q-btn>
                  <q-separator vertical inset />
                  <q-btn flat dense icon="delete_sweep" @click="clearCanvas">
                    <q-tooltip>清空画布</q-tooltip>
                  </q-btn>
                  <q-btn flat dense icon="center_focus_strong" @click="centerView">
                    <q-tooltip>居中视图</q-tooltip>
                  </q-btn>
                  <q-btn flat dense icon="zoom_in" @click="zoomIn">
                    <q-tooltip>放大</q-tooltip>
                  </q-btn>
                  <q-btn flat dense icon="zoom_out" @click="zoomOut">
                    <q-tooltip>缩小</q-tooltip>
                  </q-btn>
                </q-btn-group>
              </q-card-section>
              <q-separator />
              <div id="pipeline-editor" class="flow-container" />
            </q-card>
          </div>
        </div>
      </q-card-section>

      <!-- 添加测试面板组件 -->
      <pipeline-test-panel v-model="showTestPanel" :pipeline="pipeline" />
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useQuasar } from 'quasar'
import { Pipeline, NodeType, EdgeType, NodeConfig, EdgeConfig } from '@/services/pipeline'
import { ParamType } from '@/services/cv_operation'
import { cvOperationService } from '@/services/cv_operation'
import ParameterInput from './ParameterInput.vue'
import PipelineTestPanel from './PipelineTestPanel.vue'
import LogicFlow from '@logicflow/core'
import { RectNode, DiamondNode, CircleNode, RectNodeModel, DiamondNodeModel, CircleNodeModel, PolylineEdge, PolylineEdgeModel } from '@logicflow/core'
import '@logicflow/core/dist/index.css'
import { v4 as uuidv4 } from 'uuid'

const $q = useQuasar()

const props = defineProps<{
  modelValue: boolean
  pipeline: Partial<Pipeline>
  saving: boolean
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

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'submit': [pipeline: Partial<Pipeline>]
  'update:pipeline': [pipeline: Partial<Pipeline>]
}>()

// 编辑器状态管理
const lf = ref<LogicFlow | null>(null)
const showTestPanel = ref(false)
const operations = ref<any[]>([])
const selectedNode = ref<NodeConfig | null>(null)
const selectedEdge = ref<any>(null)
const canUndo = ref(false)
const canRedo = ref(false)
const loadingOperation = ref(false)

// 可用节点类型
const availableNodeTypes = [
  NodeType.OPERATION,
  NodeType.CONDITION,
  NodeType.PARALLEL,
  NodeType.MERGE
]

// 创建一个本地流水线数据的副本
const localPipeline = ref<Partial<Pipeline>>({
  ...props.pipeline,
  inputParams: [...(props.pipeline.inputParams || [])],
  outputParams: [...(props.pipeline.outputParams || [])],
  metadata: {
    nodes: [...(props.pipeline.metadata?.nodes || [])],
    edges: [...(props.pipeline.metadata?.edges || [])]
  }
})

// 监听props变化，更新本地数据
watch(() => props.pipeline, (newPipeline) => {
  localPipeline.value = {
    ...newPipeline,
    inputParams: [...(newPipeline.inputParams || [])],
    outputParams: [...(newPipeline.outputParams || [])],
    metadata: {
      nodes: [...(newPipeline.metadata?.nodes || [])],
      edges: [...(newPipeline.metadata?.edges || [])]
    }
  }
}, { deep: true })

// 更新本地数据并触发父组件更新
const updatePipeline = (updates: Partial<Pipeline>) => {
  localPipeline.value = {
    ...localPipeline.value,
    ...updates
  }
  emit('update:pipeline', localPipeline.value)
}

// 获取节点图标
const getNodeIcon = (nodeType: NodeType) => {
  const iconMap: Record<NodeType, string> = {
    [NodeType.START]: 'play_circle',
    [NodeType.END]: 'stop_circle',
    [NodeType.OPERATION]: 'settings',
    [NodeType.PARALLEL]: 'call_split',
    [NodeType.MERGE]: 'call_merge',
    [NodeType.CONDITION]: 'help'
  }
  return iconMap[nodeType] || 'device_hub'
}

// 获取节点标签
const getNodeLabel = (nodeType: NodeType) => {
  const labelMap: Record<NodeType, string> = {
    [NodeType.START]: '开始',
    [NodeType.END]: '结束',
    [NodeType.OPERATION]: '操作',
    [NodeType.PARALLEL]: '并行',
    [NodeType.MERGE]: '合并',
    [NodeType.CONDITION]: '条件'
  }
  return labelMap[nodeType] || '未知'
}

// 操作搜索
const selectedOperation = ref<any>(null)

// 处理操作选择改变
const handleOperationChange = async (operationId: number) => {
  if (!selectedNode.value) return

  try {
    // 获取操作详情
    const operation = await cvOperationService.getOperation(operationId)
    selectedOperation.value = operation

    // 初始化参数配置
    if (!selectedNode.value.config) {
      selectedNode.value.config = {}
    }

    if (!selectedNode.value.config.params) {
      selectedNode.value.config.params = {}
    }

    // 为每个参数设置默认配置
    operation.inputParams.forEach((param: any) => {
      if (!selectedNode.value?.config?.params[param.name]) {
        selectedNode.value!.config!.params[param.name] = {
          source: 'custom', // 默认为自定义值
          value: param.default
        }
      }
    })

    // 更新节点
    updateNodeInMetadata(selectedNode.value)

    // 更新节点显示
    if (lf.value) {
      const node = lf.value.getNodeModelById(selectedNode.value.id)
      if (node) {
        node.updateText(operation.name)
        node.setProperties({
          ...node.getProperties(),
          operationId: operationId,
        })
      }
    }
  } catch (error) {
    console.error('获取操作详情失败:', error)
    selectedOperation.value = null
    $q.notify({
      type: 'negative',
      message: '获取操作详情失败'
    })
  }
}

// 更新节点参数配置
const updateNodeParamConfig = (paramName: string, field: 'source' | 'value', newValue: any) => {
  if (!selectedNode.value) return
  
  // 创建深拷贝以避免直接修改引用
  const updatedNode = JSON.parse(JSON.stringify(selectedNode.value))
  
  // 初始化配置对象
  if (!updatedNode.config) updatedNode.config = {}
  if (!updatedNode.config.params) updatedNode.config.params = {}
  if (!updatedNode.config.params[paramName]) updatedNode.config.params[paramName] = { source: 'custom', value: null }
  
  // 更新字段
  updatedNode.config.params[paramName][field] = newValue
  
  // 如果更改了来源，重置值
  if (field === 'source' && newValue !== 'custom') {
    updatedNode.config.params[paramName].value = null
  }
  
  // 先更新选中节点以确保UI立即响应
  selectedNode.value = updatedNode
  
  // 更新元数据中的节点
  updateNodeInMetadata(updatedNode)
  
  // 更新画布上的节点
  if (lf.value) {
    const node = lf.value.getNodeModelById(updatedNode.id)
    if (node) {
      node.setProperties({
        ...node.getProperties(),
        config: updatedNode.config
      })
    }
  }
  
  // 强制触发UI更新
  nextTick(() => {
    console.log(`参数 ${paramName} 的 ${field} 已更新为:`, newValue)
  })
}

// Create a safer getter that doesn't mutate
const getParamConfigValue = (node: NodeConfig | null, paramName: string, field: 'source' | 'value') => {
  if (!node || !node.config || !node.config.params || !node.config.params[paramName]) {
    return field === 'source' ? 'custom' : null
  }
  return node.config.params[paramName][field]
}

// 获取参数来源选项
const getParamSourceOptions = (param: any) => {
  const options = [
    { label: '自定义值', value: 'custom' }
  ]

  // 添加流水线输入参数作为可能的来源
  localPipeline.value.inputParams?.forEach(input => {
    if (input.type === param.type) {
      options.push({
        label: `流水线输入: ${input.name}`,
        value: `input:${input.name}`
      })
    }
  })

  // 添加上一个节点的输出作为可能的来源
  // 这需要分析流水线的连接关系，确定上游节点
  const previousNodes = getPreviousNodes(selectedNode.value?.id)
  previousNodes.forEach(node => {
    if (node.type === NodeType.OPERATION && node.operationId) {
      // 这里需要根据 operationId 获取操作的输出参数
      // 简化处理，实际实现可能需要额外的API调用
      const operation = operations.value.find(op => op.id === node.operationId)
      if (operation?.outputParams) {
        operation.outputParams.forEach((output: { name: string; type: ParamType }) => {
          if (output.type === param.type) {
            options.push({
              label: `${node.name || getNodeLabel(node.type)} 输出: ${output.name}`,
              value: `node:${node.id}:${output.name}`
            })
          }
        })
      }
    }
  })

  return options
}

// 获取前置节点
const getPreviousNodes = (nodeId: string | undefined): NodeConfig[] => {
  if (!nodeId || !localPipeline.value.metadata) return []

  const incomingEdges = localPipeline.value.metadata.edges.filter(edge => edge.target === nodeId)
  return incomingEdges.map(edge => {
    const sourceNode = localPipeline.value.metadata?.nodes.find(node => node.id === edge.source)
    return sourceNode as NodeConfig
  }).filter(Boolean)
}

// 获取参数类型颜色
const getTypeColor = (type: ParamType) => {
  const colorMap: Record<ParamType, string> = {
    [ParamType.TEXT]: 'blue',
    [ParamType.NUMBER]: 'green',
    [ParamType.BOOLEAN]: 'purple',
    [ParamType.IMAGE]: 'red',
    [ParamType.ARRAY]: 'orange',
    [ParamType.OBJECT]: 'teal'
  }
  return colorMap[type] || 'grey'
}

// 加载操作列表
const loadOperations = async () => {
  try {
    operations.value = await cvOperationService.getOperations()
  } catch (error) {
    console.error('加载操作列表失败:', error)
    $q.notify({
      type: 'negative',
      message: '加载操作列表失败'
    })
  }
}

// 添加 initLogicFlow 函数
const initLogicFlow = async () => {
  await nextTick()
  const container = document.getElementById('pipeline-editor')
  if (!container) {
    console.error('Pipeline editor container not found')
    return
  }

  try {
    // 注册自定义节点和边
    class OperationNodeModel extends RectNodeModel {
      initNodeData(data: any) {
        super.initNodeData(data)
        this.targetRules.push({
          message: '操作节点只能有一个入度',
          validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
            return this.incoming.edges.length < 1
          }
        })
        this.sourceRules.push({
          message: '操作节点只能有一个出度',
          validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
            return this.outgoing.edges.length < 1
          }
        })
      }

      getNodeStyle() {
        const style = super.getNodeStyle()
        style.stroke = '#1976d2'  // 主题蓝色
        style.strokeWidth = 2
        style.fill = '#1e293b'  // 深色背景
        return style
      }
      getTextStyle() {
        const style = super.getTextStyle();
        style.fill = '#fff';
        style.fontSize = 20;
        return style;
      }
    }

    class ConditionNodeModel extends DiamondNodeModel {
      initNodeData(data: any) {
        super.initNodeData(data)

        this.targetRules.push({
          message: '条件节点只能有一个入度',
          validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
            return this.incoming.edges.length < 1
          }
        })
        this.sourceRules.push({
          message: '条件节点只能有两个出度',
          validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
            return this.outgoing.edges.length < 2
          }
        })
      }

      getNodeStyle() {
        const style = super.getNodeStyle()
        style.stroke = '#ff9800'  // 橙色
        style.strokeWidth = 2
        style.fill = '#1e293b'
        return style
      }
      getTextStyle() {
        const style = super.getTextStyle();
        style.fill = '#fff';
        style.fontSize = 20;
        return style;
      }
    }

    class ParallelNodeModel extends RectNodeModel {
      initNodeData(data: any) {
        super.initNodeData(data)

        this.targetRules.push({
          message: '并行节点只能有一个入度，可以有多个出度',
          validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
            return this.incoming.edges.length < 1
          }
        })
      }

      getNodeStyle() {
        const style = super.getNodeStyle()
        style.stroke = '#4caf50'  // 绿色
        style.strokeWidth = 2
        style.fill = '#1e293b'
        style.rx = 5  // 圆角矩形
        style.ry = 5
        return style
      }
      getTextStyle() {
        const style = super.getTextStyle();
        style.fill = '#fff';
        style.fontSize = 20;
        return style;
      }
    }

    class MergeNodeModel extends RectNodeModel {
      initNodeData(data: any) {
        super.initNodeData(data)

        this.sourceRules.push({
          message: '合并节点只能有一个出度，可以有多个入度',
          validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
            return this.outgoing.edges.length < 1
          }
        })
      }

      getNodeStyle() {
        const style = super.getNodeStyle()
        style.stroke = '#9c27b0'  // 紫色
        style.strokeWidth = 2
        style.fill = '#1e293b'
        style.rx = 5
        style.ry = 5
        return style
      }
      getTextStyle() {
        const style = super.getTextStyle();
        style.fill = '#fff';
        style.fontSize = 20;
        return style;
      }
    }

    class StartNodeModel extends CircleNodeModel {
      initNodeData(data: any) {
        super.initNodeData(data)

        // Start nodes can only have outgoing connections
        const startRules = {
          message: '开始节点只能有出度，不能有入度',
          validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
            return this.outgoing.edges.length < 1 && this.incoming.edges.length === 0
          }
        }
        this.sourceRules.push(startRules)
        this.targetRules.push(startRules)
      }

      getNodeStyle() {
        const style = super.getNodeStyle()
        style.stroke = '#4caf50'  // 绿色
        style.strokeWidth = 2
        style.fill = '#1e293b'
        return style
      }
      getTextStyle() {
        const style = super.getTextStyle();
        style.fill = '#fff';
        style.fontSize = 20;
        return style;
      }
    }

    class EndNodeModel extends CircleNodeModel {
      initNodeData(data: any) {
        super.initNodeData(data)

        // End nodes can only have incoming connections
        const endRules = {
          message: '结束节点只能有入度，不能有出度',
          validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
            return this.incoming.edges.length < 1 && this.outgoing.edges.length === 0
          }
        }
        this.sourceRules.push(endRules)
        this.targetRules.push(endRules)
      }

      getNodeStyle() {
        const style = super.getNodeStyle()
        style.stroke = '#f44336'  // 红色
        style.strokeWidth = 2
        style.fill = '#1e293b'
        return style
      }
      getTextStyle() {
        const style = super.getTextStyle();
        style.fill = '#fff';
        style.fontSize = 20;
        return style;
      }
    }

    class NormalEdgeModel extends PolylineEdgeModel {
      getEdgeStyle() {
        const style = super.getEdgeStyle()
        style.stroke = '#666'
        return style
      }
    }

    // 创建 LogicFlow 实例
    lf.value = new LogicFlow({
      container: container,
      grid: true,
      background: {
        color: '#1e1e1e'
      },
      nodeTextEdit: false,
      edgeTextEdit: false,
      edgeType: EdgeType.NORMAL,
      history: true // 启用历史功能，支持撤销/重做
    })

    // 注册节点
    lf.value.register({
      type: NodeType.OPERATION,
      view: RectNode,
      model: OperationNodeModel
    })
    lf.value.register({
      type: NodeType.CONDITION,
      view: DiamondNode,
      model: ConditionNodeModel
    })
    lf.value.register({
      type: NodeType.PARALLEL,
      view: RectNode,
      model: ParallelNodeModel
    })
    lf.value.register({
      type: NodeType.MERGE,
      view: RectNode,
      model: MergeNodeModel
    })
    lf.value.register({
      type: NodeType.START,
      view: CircleNode,
      model: StartNodeModel
    })
    lf.value.register({
      type: NodeType.END,
      view: CircleNode,
      model: EndNodeModel
    })

    // 注册边类型
    lf.value.register({
      type: EdgeType.TRUE,
      view: PolylineEdge,
      model: NormalEdgeModel
    })
    lf.value.register({
      type: EdgeType.FALSE,
      view: PolylineEdge,
      model: NormalEdgeModel
    })
    lf.value.register({
      type: EdgeType.NORMAL,
      view: PolylineEdge,
      model: NormalEdgeModel
    })

    // 初始化流水线设计器和绑定事件
    initializeCanvas()
    bindEvents()

  } catch (error) {
    console.error('初始化LogicFlow失败:', error)
    $q.notify({
      type: 'negative',
      message: '初始化流水线设计器失败'
    })
  }
}

// 修改 initializeCanvas 函数
const initializeCanvas = () => {
  if (!lf.value || !localPipeline.value.metadata) return

  try {
    // 清空画布
    lf.value.clearData()
    // 加载节点
    if (localPipeline.value.metadata.nodes.length > 0) {
      // 遍历添加所有节点
      localPipeline.value.metadata.nodes.forEach(node => {
        // 确保位置是有效的数字
        const x = typeof node.position.x === 'number' ? node.position.x : 100
        const y = typeof node.position.y === 'number' ? node.position.y : 100

        lf.value?.addNode({
          id: node.id,
          type: node.type,
          x: x,
          y: y,
          text: node.name || getNodeLabel(node.type),
          properties: {
            nodeType: node.type,
            config: node.config || {},
            operationId: node.operationId || null
          }
        })
      })

      // 加载连接线
      if (localPipeline.value.metadata.edges.length > 0) {
        // 遍历添加所有边
        localPipeline.value.metadata.edges.forEach(edge => {
          lf.value?.addEdge({
            id: edge.id,
            type: edge.type || EdgeType.NORMAL,
            sourceNodeId: edge.source,
            targetNodeId: edge.target,
            text: edge.type === EdgeType.TRUE ? '是' :
              edge.type === EdgeType.FALSE ? '否' : '',
            properties: {
              edgeType: edge.type
            }
          })
        })
      }

      // 调整画布视图以包含所有节点
      lf.value.fitView()
    } else {
      // 如果没有现有节点，则创建默认的开始和结束节点
      const startNode = {
        id: 'start',
        type: NodeType.START,
        x: 100,
        y: 100,
        text: getNodeLabel(NodeType.START),
        properties: {
          nodeType: NodeType.START
        }
      }

      const endNode = {
        id: 'end',
        type: NodeType.END,
        x: 500,
        y: 100,
        text: getNodeLabel(NodeType.END),
        properties: {
          nodeType: NodeType.END
        }
      }

      lf.value.addNode(startNode)
      lf.value.addNode(endNode)

      // 更新元数据
      localPipeline.value.metadata = {
        nodes: [
          {
            id: 'start',
            type: NodeType.START,
            position: { x: 100, y: 100 },
            config: {}
          },
          {
            id: 'end',
            type: NodeType.END,
            position: { x: 500, y: 100 },
            config: {}
          }
        ],
        edges: []
      }

      updatePipeline({ metadata: localPipeline.value.metadata })
    }
  } catch (error) {
    console.error('初始化画布失败:', error)
    $q.notify({
      type: 'negative',
      message: '初始化画布失败'
    })
  }
}

// Method to handle node dragging from toolbox
const startDrag = (nodeType: NodeType) => {
  if (!lf.value) return

  // 生成唯一ID
  const nodeId = `${nodeType}_${uuidv4().substring(0, 8)}`

  // 获取画布中心位置
  const centerPosition = lf.value.getPointByClient(
    window.innerWidth / 2,
    window.innerHeight / 2
  ).canvasOverlayPosition

  // 确保位置是有效的数字
  const x = centerPosition && typeof centerPosition.x === 'number' ? centerPosition.x : 300
  const y = centerPosition && typeof centerPosition.y === 'number' ? centerPosition.y : 200

  // 创建节点配置
  const nodeConfig = {
    id: nodeId,
    type: nodeType,
    text: getNodeLabel(nodeType),
    x: x,
    y: y,
    properties: {
      nodeType: nodeType
    }
  }

  // 添加节点到画布
  lf.value.addNode(nodeConfig)

  // 更新元数据
  const newNode: NodeConfig = {
    id: nodeId,
    type: nodeType,
    name: getNodeLabel(nodeType),
    position: { x: x, y: y },
    config: {}
  }

  if (!localPipeline.value.metadata) {
    localPipeline.value.metadata = { nodes: [], edges: [] }
  }

  localPipeline.value.metadata.nodes.push(newNode)
  updatePipeline({ metadata: localPipeline.value.metadata })

  // 选中新节点
  selectedNode.value = newNode
}

// 撤销操作
const undo = () => {
  if (lf.value) {
    lf.value.undo()
    updateUndoRedoState()
  }
}

// 重做操作
const redo = () => {
  if (lf.value) {
    lf.value.redo()
    updateUndoRedoState()
  }
}

// 删除选中的节点或边
const deleteSelected = () => {
  if (!lf.value) return

  if (selectedNode.value) {
    // Checks for START/END nodes remain the same
    if (selectedNode.value.type === NodeType.START || selectedNode.value.type === NodeType.END) {
      $q.notify({
        type: 'warning',
        message: '不能删除开始和结束节点'
      })
      return
    }

    // Delete node from LogicFlow
    lf.value.deleteNode(selectedNode.value.id)
    
    // Delete node from metadata
    if (localPipeline.value.metadata) {
      localPipeline.value.metadata.nodes = localPipeline.value.metadata.nodes.filter(
        node => node.id !== selectedNode.value?.id
      )
      
      // Also remove any edges connected to this node
      localPipeline.value.metadata.edges = localPipeline.value.metadata.edges.filter(
        edge => edge.source !== selectedNode.value?.id && edge.target !== selectedNode.value?.id
      )
      
      updatePipeline({ metadata: localPipeline.value.metadata })
    }
    
    selectedNode.value = null
  } else if (selectedEdge.value) {
    // Delete edge from LogicFlow
    lf.value.deleteEdge(selectedEdge.value.id)
    
    // Delete edge from metadata (this should also be handled by the edge:delete event,
    // but we include it here for completeness)
    if (localPipeline.value.metadata) {
      localPipeline.value.metadata.edges = localPipeline.value.metadata.edges.filter(
        edge => edge.id !== selectedEdge.value?.id
      )
      updatePipeline({ metadata: localPipeline.value.metadata })
    }
    
    selectedEdge.value = null
  }
}

// 清空画布
const clearCanvas = () => {
  if (!lf.value) return

  $q.dialog({
    title: '确认清空',
    message: '确定要清空流水线设计吗？此操作不可恢复。',
    cancel: true,
    persistent: true
  }).onOk(() => {
    // 只保留开始和结束节点
    if (localPipeline.value.metadata) {
      const startNode = localPipeline.value.metadata.nodes.find(n => n.type === NodeType.START)
      const endNode = localPipeline.value.metadata.nodes.find(n => n.type === NodeType.END)

      localPipeline.value.metadata.nodes = []
      localPipeline.value.metadata.edges = []

      if (startNode) localPipeline.value.metadata.nodes.push(startNode)
      if (endNode) localPipeline.value.metadata.nodes.push(endNode)

      updatePipeline({ metadata: localPipeline.value.metadata })

      // 重新初始化画布
      initializeCanvas()
    }
  })
}

// 居中视图
const centerView = () => {
  if (lf.value) {
    lf.value.fitView()
  }
}

// 放大
const zoomIn = () => {
  if (lf.value) {
    const zoomStep = 0.1
    const currentZoom = lf.value.getTransform().SCALE_X
    lf.value.zoom(currentZoom + zoomStep)
  }
}

// 缩小
const zoomOut = () => {
  if (lf.value) {
    const zoomStep = 0.1
    const currentZoom = lf.value.getTransform().SCALE_X
    if (currentZoom > 0.2) { // 防止缩放太小
      lf.value.zoom(currentZoom - zoomStep)
    }
  }
}

// 更新撤销/重做状态
const updateUndoRedoState = () => {
  if (lf.value) {
    canUndo.value = lf.value.history && lf.value.history.undoAble()
    canRedo.value = lf.value.history && lf.value.history.redoAble()
  }
}

// Methods
const addInputParam = () => {
  if (!localPipeline.value.inputParams) {
    localPipeline.value.inputParams = []
  }
  const idx = localPipeline.value.inputParams.length + 1
  const newParam = {
    name: `input_${idx}`,
    type: ParamType.TEXT,
    description: '',
    default: undefined,
    required: false
  }
  localPipeline.value.inputParams.push(newParam)
  updatePipeline({ inputParams: localPipeline.value.inputParams })
}

const addOutputParam = () => {
  if (!localPipeline.value.outputParams) {
    localPipeline.value.outputParams = []
  }
  const idx = localPipeline.value.outputParams.length + 1
  const newParam = {
    name: `output_${idx}`,
    type: ParamType.TEXT,
    description: '',
    default: undefined,
    required: false
  }
  localPipeline.value.outputParams.push(newParam)
  updatePipeline({ outputParams: localPipeline.value.outputParams })
}

const removeInputParam = (index: number) => {
  if (!localPipeline.value.inputParams) return
  localPipeline.value.inputParams.splice(index, 1)
  updatePipeline({ inputParams: localPipeline.value.inputParams })
}

const removeOutputParam = (index: number) => {
  if (!localPipeline.value.outputParams) return
  localPipeline.value.outputParams.splice(index, 1)
  updatePipeline({ outputParams: localPipeline.value.outputParams })
}

const handleClose = () => {
  emit('update:modelValue', false)
}

// 在保存流水线前验证所有操作节点
const validatePipeline = () => {
  if (!localPipeline.value.metadata) return false;
  
  const operationNodes = localPipeline.value.metadata.nodes.filter(
    node => node.type === NodeType.OPERATION
  );
  
  for (const node of operationNodes) {
    if (!node.operationId) {
      $q.notify({
        type: 'negative',
        message: `操作节点 "${node.name || '未命名'}" 没有选择操作`
      });
      return false;
    }
  }
  
  return true;
}

// 在提交前调用验证
const handleSubmit = () => {
  if (!validatePipeline()) return;
  
  // 同步画布到元数据
  syncCanvasToMetadata()

  const pipelineData = {
    ...localPipeline.value,
    metadata: localPipeline.value.metadata
  }

  emit('submit', pipelineData)
}

// 监听对话框显示状态
watch(() => props.modelValue, async (newVal) => {
  if (newVal) {
    await nextTick()
    initLogicFlow()
  }
})

// 监听选中节点变化
watch(() => selectedNode.value, (newNode) => {
  if (newNode && lf.value) {
    lf.value.selectElementById(newNode.id)
  }
})

// 监听节点属性变化
watch(() => selectedNode.value, () => {
  if (selectedNode.value) {
    updateNodeInMetadata(selectedNode.value)
  }
}, { deep: true })

// 生命周期钩子
onMounted(() => {
  loadOperations()
  nextTick(() => {
    if (props.modelValue) {
      initLogicFlow()
    }
  })
})

onBeforeUnmount(() => {
  const editorContainer = document.querySelector('.editor-dialog')
  if (editorContainer) {
    editorContainer.removeEventListener('keydown', handleKeyDown, true)
  }
  if (lf.value) {
    lf.value.off('node:click', () => { })
    lf.value.off('edge:click', () => { })
    lf.value.off('blank:click', () => { })
    lf.value.off('edge:add', () => { })
    lf.value.off('edge:delete', () => { })
    lf.value.off('node:delete', () => { })
    lf.value.off('history:change', () => { })
    lf.value.off('connection:not-allowed', () => { })
  }
})

// 修改 bindEvents 函数，添加快捷键和边选择的支持
const bindEvents = () => {
  if (!lf.value) return

  // 节点选择事件
  lf.value.on('node:click', async ({ data }) => {
    const nodeId = data.id
    const node = localPipeline.value.metadata?.nodes.find(n => n.id === nodeId)
    if (node) {
      // Initialize END node config if needed
      if (node.type === NodeType.END) {
        if (!node.config) node.config = {}
        if (!node.config.outputMappings) node.config.outputMappings = {}
      }
      
      selectedNode.value = { ...node }
      selectedEdge.value = null
      
      // 特殊处理操作节点：加载操作详情
      if (node.type === NodeType.OPERATION && node.operationId) {
        try {
          loadingOperation.value = true
          // 获取操作详情
          const operation = await cvOperationService.getOperation(node.operationId)
          selectedOperation.value = operation
        } catch (error) {
          console.error('获取操作详情失败:', error)
          selectedOperation.value = null
          $q.notify({
            type: 'negative',
            message: '加载操作详情失败'
          })
        } finally {
          loadingOperation.value = false
        }
      } else {
        // 非操作节点，清空当前选中的操作
        selectedOperation.value = null
      }
    }
    updateUndoRedoState()
  })

  // 边选择事件
  lf.value.on('edge:click', ({ data }) => {
    selectedEdge.value = data
    selectedNode.value = null
    updateUndoRedoState()
  })

  // 画布点击事件，取消选择
  lf.value.on('blank:click', () => {
    selectedNode.value = null
    selectedEdge.value = null
    updateUndoRedoState()
  })

  // 边连接事件
  lf.value.on('connection:not-allowed', ({ msg }) => {
    $q.notify({
      type: 'warning',
      message: msg
    })
  })

  // 所有历史操作事件
  lf.value.on('history:change', () => {
    updateUndoRedoState()
  })

  // 添加键盘快捷键支持
  setupKeyboardEvents()

  // Edge add event
  lf.value.on('edge:add', ({ data }) => {
    if (!localPipeline.value.metadata) return

    // Add the new edge to metadata
    const newEdge: EdgeConfig = {
      id: data.id,
      source: data.sourceNodeId,
      target: data.targetNodeId,
      type: data.properties?.edgeType || EdgeType.NORMAL
    }
    
    // Check if edge already exists to avoid duplicates
    const edgeExists = localPipeline.value.metadata.edges.some(e => e.id === newEdge.id)
    if (!edgeExists) {
      localPipeline.value.metadata.edges.push(newEdge)
      updatePipeline({ metadata: localPipeline.value.metadata })
    }
  })

  // Edge delete event
  lf.value.on('edge:delete', ({ data }) => {
    if (!localPipeline.value.metadata) return
    
    // Remove the edge from metadata
    const edgeId = data.id
    localPipeline.value.metadata.edges = localPipeline.value.metadata.edges.filter(
      edge => edge.id !== edgeId
    )
    updatePipeline({ metadata: localPipeline.value.metadata })
  })

  // Node move event
  lf.value.on('node:drag', ({ data }) => {
    if (!localPipeline.value.metadata) return
    
    // Update node position in metadata
    const nodeId = data.id
    const nodeIndex = localPipeline.value.metadata.nodes.findIndex(node => node.id === nodeId)
    
    if (nodeIndex !== -1) {
      localPipeline.value.metadata.nodes[nodeIndex].position = { 
        x: data.x, 
        y: data.y 
      }
      // We don't call updatePipeline here to avoid too many updates during dragging
    }
  })

  // After node drag is complete, update the pipeline
  lf.value.on('node:dragend', () => {
    if (localPipeline.value.metadata) {
      updatePipeline({ metadata: localPipeline.value.metadata })
    }
  })
}

// 修改键盘事件处理
const setupKeyboardEvents = () => {
  // 获取整个编辑器容器元素
  const editorContainer = document.querySelector('.editor-dialog')
  
  if (!editorContainer) return
  
  // 移除任何现有的事件监听器，避免重复
  editorContainer.removeEventListener('keydown', handleKeyDown)
  
  // 添加键盘事件监听器到整个编辑器容器，使用捕获阶段
  editorContainer.addEventListener('keydown', handleKeyDown, true)
  
  console.log('Keyboard events setup completed')
}

// 键盘事件处理函数
const handleKeyDown = (e: Event) => {
  // 将事件转换为 KeyboardEvent
  const keyEvent = e as KeyboardEvent;
  
  // 如果编辑器不可见或 LogicFlow 实例不存在，则不处理
  if (!props.modelValue || !lf.value) return
  
  // 忽略输入框中的键盘事件
  if (keyEvent.target instanceof HTMLInputElement || 
      keyEvent.target instanceof HTMLTextAreaElement || 
      keyEvent.target instanceof HTMLSelectElement) {
    return
  }
  
  console.log('Key pressed:', keyEvent.key, 'Ctrl:', keyEvent.ctrlKey, 'Meta:', keyEvent.metaKey, 'Shift:', keyEvent.shiftKey)
  
  // 撤销 (Ctrl+Z 或 Command+Z)
  if ((keyEvent.ctrlKey || keyEvent.metaKey) && keyEvent.key === 'z' && !keyEvent.shiftKey) {
    console.log('Undo triggered')
    undo()
    keyEvent.preventDefault()
    keyEvent.stopPropagation()
    return
  }
  
  // 重做 (Ctrl+Shift+Z 或 Command+Shift+Z)
  if ((keyEvent.ctrlKey || keyEvent.metaKey) && keyEvent.shiftKey && keyEvent.key === 'z') {
    console.log('Redo triggered')
    redo()
    keyEvent.preventDefault()
    keyEvent.stopPropagation()
    return
  }
  
  // 删除键 (Delete 或 Backspace) - 只在有选中元素时触发
  if ((keyEvent.key === 'Delete' || keyEvent.key === 'Backspace') && (selectedNode.value || selectedEdge.value)) {
    console.log('Delete triggered')
    deleteSelected()
    keyEvent.preventDefault()
    keyEvent.stopPropagation()
    return
  }
}

// 修改 updateNodeInMetadata 函数
const updateNodeInMetadata = (updatedNode: NodeConfig) => {
  if (!localPipeline.value.metadata) return

  const nodeIndex = localPipeline.value.metadata.nodes.findIndex(node => node.id === updatedNode.id)
  if (nodeIndex === -1) return

  localPipeline.value.metadata.nodes[nodeIndex] = { ...updatedNode }

  // 更新 LogicFlow 节点文本
  if (lf.value) {
    const lfNode = lf.value.getNodeModelById(updatedNode.id)
    if (lfNode) {
      // 更新节点文本显示，使用 updateText 而不是 setText
      lfNode.updateText(updatedNode.name || getNodeLabel(updatedNode.type))
    }
  }

  // 通知父组件元数据已更新
  updatePipeline({ metadata: localPipeline.value.metadata })
}

// 同步画布到元数据
const syncCanvasToMetadata = () => {
  if (!lf.value) return
  const graphData = lf.value.getGraphData() as LogicFlow.GraphData;
  // 同步节点
  const nodes: NodeConfig[] = graphData.nodes.map(node => {
    // 确保 operationId 是数字
    let operationId = node.properties?.operationId || node?.operationId;
    if (operationId !== undefined && operationId !== null) {
      operationId = Number(operationId);
    }
    
    return {
      id: node.id,
      type: node.properties?.nodeType || NodeType.OPERATION,
      name: node.text?.value || '',
      operationId: operationId,
      config: node.properties?.config || {},
      position: { x: node.x, y: node.y }
    }
  })

  // 同步边
  const edges: EdgeConfig[] = graphData.edges.map(edge => {
    return {
      id: edge.id,
      source: edge.sourceNodeId,
      target: edge.targetNodeId,
      type: edge.properties?.edgeType || EdgeType.NORMAL
    }
  })

  // 更新元数据
  localPipeline.value.metadata = { nodes, edges }
  updatePipeline({ metadata: localPipeline.value.metadata })
}

// 添加新的过滤方法
const filterOperations = (val: string, update: (fn: () => void) => void) => {
  if (val === '') {
    update(() => {
      // 当输入为空时显示所有操作
    })
    return
  }

  update(() => {
    // 直接过滤操作列表
    // 不需要更新 filteredOperations 变量，因为这个过滤是由 QSelect 组件内部处理的
  })
}

// Add this function to get all possible outputs for the END node
const getEndNodeOutputOptions = () => {
  if (!localPipeline.value.metadata) return []
  
  const endNode = localPipeline.value.metadata.nodes.find(node => node.type === NodeType.END)
  if (!endNode) return []
  
  const options = []
  
  // Get all nodes that connect to the END node
  const previousNodes = getPreviousNodes(endNode.id)
  
  // For each previous node, get its outputs
  previousNodes.forEach(node => {
    if (node.type === NodeType.OPERATION && node.operationId) {
      const operation = operations.value.find(op => op.id === node.operationId)
      if (operation?.outputParams) {
        operation.outputParams.forEach((output: { name: string; type: ParamType }) => {
          options.push({
            label: `${node.name || getNodeLabel(node.type)} 输出: ${output.name}`,
            value: `node:${node.id}:${output.name}`,
            type: output.type
          })
        })
      }
    }
  })
  
  return options
}

// Get the current output mapping for an END node parameter
const getEndNodeOutputMapping = (paramName: string) => {
  if (!selectedNode.value || selectedNode.value.type !== NodeType.END) return null
  
  if (!selectedNode.value.config) return null
  if (!selectedNode.value.config.outputMappings) return null
  
  const mapping = selectedNode.value.config.outputMappings[paramName] || null
  console.log(`Getting output mapping for ${paramName}: ${mapping}`)
  return mapping
}

// Update the output mapping for an END node parameter
const updateEndNodeOutputMapping = (paramName: string, value: string | null) => {
  if (!selectedNode.value || selectedNode.value.type !== NodeType.END) return
  
  // Create a deep copy to avoid direct mutations
  const updatedNode = JSON.parse(JSON.stringify(selectedNode.value))
  
  // Initialize if needed
  if (!updatedNode.config) updatedNode.config = {}
  if (!updatedNode.config.outputMappings) updatedNode.config.outputMappings = {}
  
  if (value === null) {
    // Remove mapping if value is null
    delete updatedNode.config.outputMappings[paramName]
  } else {
    // Set the mapping
    updatedNode.config.outputMappings[paramName] = value
  }
  
  // Update the selected node first to ensure UI reactivity
  selectedNode.value = updatedNode
  
  // Update the node in metadata
  updateNodeInMetadata(updatedNode)
  
  // Update the LogicFlow node properties
  if (lf.value) {
    const node = lf.value.getNodeModelById(updatedNode.id)
    if (node) {
      node.setProperties({
        ...node.getProperties(),
        config: updatedNode.config
      })
    }
  }
  
  // Force a UI update by logging the change
  console.log(`Updated output mapping for ${paramName} to ${value}`)
}
</script>
<style lang="scss">
/* Basic LogicFlow styles */
.lf-graph {
  width: 100%;
  height: 100%;
  background: var(--dark-page);
}

.lf-node {
  cursor: pointer;
}

.lf-edge {
  cursor: pointer;
}
</style>

<style lang="scss" scoped>
/* Add this at the top of your style section */
/* Basic LogicFlow styles */
.lf-graph {
  width: 100%;
  height: 100%;
  background: var(--dark-page);
}

.lf-node {
  cursor: pointer;
}

.lf-edge {
  cursor: pointer;
}

/* Your existing styles continue below */
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
    background: linear-gradient(45deg,
        rgba(255, 255, 255, 0.03) 25%,
        transparent 25%,
        transparent 75%,
        rgba(255, 255, 255, 0.03) 75%);
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

      // 右侧流水线画布样式
      .flow-panel {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 0;

        .flow-editor-card {
          flex: 1;
          display: flex;
          flex-direction: column;
          margin: 16px;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          overflow: hidden;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);

          .flow-editor-header {
            background: linear-gradient(180deg, var(--dark-card) 0%, var(--dark-card-header) 100%);
            padding: 8px 16px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;

            .text-subtitle2 {
              font-weight: 500;
              color: var(--text-primary);
            }
          }

          .flow-container {
            flex: 1;
            min-height: 0;
            background: var(--dark-page);
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
            background: linear-gradient(180deg,
                var(--dark-card) 0%,
                rgba(25, 118, 210, 0.1) 100%);
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

// 节点工具箱样式
.node-tool {
  cursor: move;
  transition: all 0.2s ease;
  border: 1px solid var(--border-color);
  background: var(--dark-card);

  &:hover {
    background: linear-gradient(180deg,
        var(--dark-card) 0%,
        rgba(25, 118, 210, 0.1) 100%);
    border-color: var(--primary);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

.operation-params {
  background: var(--dark-card-header);
  border: 1px solid var(--border-color);

  :deep(.q-item) {
    padding: 12px;
    background: var(--dark-card);
    margin-bottom: 4px;

    &:last-child {
      margin-bottom: 0;
    }

    &:hover {
      background: linear-gradient(180deg,
          var(--dark-card) 0%,
          rgba(25, 118, 210, 0.1) 100%);
    }
  }
}
</style>