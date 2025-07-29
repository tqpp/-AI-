<template>
  <div class="ocr-annotator-container">
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

      <!-- 矩形标注按钮 -->
      <q-btn round flat dense :color="isDrawing ? 'negative' : 'white'"
        icon="rectangle" @click="activateDrawingTool()">
        <q-tooltip>{{ t('annotator.tools.character') }}</q-tooltip>
      </q-btn>

      <!-- 取消绘制按钮 -->
      <q-btn round flat dense color="negative" icon="close" @click="cancelDrawing" v-if="isDrawing">
        <q-tooltip>{{ t('annotator.controls.cancelDrawing') }}</q-tooltip>
      </q-btn>

      <div class="control-divider-vertical"></div>

      <!-- 删除按钮 -->
      <q-btn round flat dense 
        :color="selectedAnnotation ? 'negative' : 'white'" 
        icon="delete" 
        @click="deleteSelected"
        :disable="!selectedAnnotation">
        <q-tooltip>{{ t('annotator.controls.deleteSelectedChar', { char: selectedAnnotation ? getAnnotationLabel(selectedAnnotation) : '' }) }}</q-tooltip>
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

    <!-- 字符选择面板 -->
    <div class="character-panel">
      <div class="character-panel-header">
        <div class="text-white text-caption">{{ t('annotator.ocr.currentChar') }}:</div>
        <q-input 
          v-model="currentCharacter" 
          dense 
          dark 
          bg-color="rgba(255,255,255,0.1)"
          class="character-input"
          maxlength="1"
          :rules="[val => val.length === 1 || t('annotator.ocr.singleCharRequired')]">
          <template v-slot:append>
            <q-btn round flat dense icon="edit" size="xs" @click="showCharacterSelector = true">
              <q-tooltip>{{ t('annotator.ocr.selectChar') }}</q-tooltip>
            </q-btn>
          </template>
        </q-input>
      </div>
      
      <div class="recent-characters">
        <div class="text-white text-caption q-mb-xs">{{ t('annotator.ocr.commonChars') }}:</div>
        <div class="character-chips">
          <q-chip 
            v-for="char in recentCharacters" 
            :key="char"
            dense
            clickable
            color="primary"
            text-color="white"
            :selected="currentCharacter === char"
            @click="currentCharacter = char">
            {{ char }}
          </q-chip>
          <q-chip 
            dense
            clickable
            outline
            color="white"
            @click="showCharacterSelector = true">
            <q-icon name="add" size="xs" class="q-mr-xs" />
            {{ t('annotator.ocr.more') }}
          </q-chip>
        </div>
      </div>
    </div>

    <!-- OpenSeadragon viewer container -->
    <div id="osd-container" ref="container" class="osd-container"></div>

    <!-- 标注列表 -->
    <div class="annotation-list">
      <q-scroll-area style="height: 100%;">
        <q-list separator>
          <q-item v-for="annotation in annotations" :key="annotation.id" 
            clickable 
            :active="selectedAnnotation && selectedAnnotation.id === annotation.id"
            @click="selectAnnotationById(annotation.id)"
            dense>
            <q-item-section avatar>
              <q-avatar size="24px" color="primary" text-color="white">
                {{ getAnnotationLabel(annotation) }}
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ t('annotator.ocr.char') }}: {{ getAnnotationLabel(annotation) }}</q-item-label>
              <q-item-label caption>
                {{ t('annotator.ocr.position') }}: {{ formatBounds(annotation) }}
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-btn flat round dense size="sm" icon="delete" color="negative" 
                @click.stop="deleteAnnotation(annotation.id)">
                <q-tooltip>{{ t('common.delete') }}</q-tooltip>
              </q-btn>
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
    </div>

    <!-- 字符选择对话框 -->
    <q-dialog v-model="showCharacterSelector">
      <q-card style="min-width: 350px" dark>
        <q-card-section>
          <div class="text-h6">{{ t('annotator.ocr.selectCharTitle') }}</div>
        </q-card-section>
        
        <q-card-section>
          <q-input 
            v-model="currentCharacter" 
            :label="t('annotator.ocr.inputChar')" 
            maxlength="1"
            autofocus
            :rules="[val => val.length === 1 || t('annotator.ocr.singleCharRequired')]">
          </q-input>
          
          <div class="q-mt-md">
            <div class="text-subtitle2 q-mb-sm">{{ t('annotator.ocr.commonCharSets') }}</div>
            <div class="character-grid">
              <q-btn v-for="char in commonCharacterSets.digits" :key="'digit-'+char"
                :label="char" 
                flat 
                dense 
                color="primary"
                class="character-button"
                @click="selectCharacter(char)"/>
            </div>
            
            <div class="character-grid q-mt-sm">
              <q-btn v-for="char in commonCharacterSets.letters" :key="'letter-'+char"
                :label="char" 
                flat 
                dense 
                color="purple"
                class="character-button"
                @click="selectCharacter(char)"/>
            </div>
            
            <div class="character-grid q-mt-sm">
              <q-btn v-for="char in commonCharacterSets.punctuation" :key="'punct-'+char"
                :label="char" 
                flat 
                dense 
                color="deep-orange"
                class="character-button"
                @click="selectCharacter(char)"/>
            </div>
            
            <div class="q-mt-sm">
              <div class="text-subtitle2">{{ t('annotator.ocr.recentlyUsed') }}</div>
              <div class="character-grid">
                <q-btn v-for="char in recentCharacters" :key="'recent-'+char"
                  :label="char" 
                  flat 
                  dense 
                  color="teal"
                  class="character-button"
                  @click="selectCharacter(char)"/>
              </div>
            </div>
          </div>
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat :label="t('common.cancel')" v-close-popup />
          <q-btn flat :label="t('common.confirm')" color="primary" 
            v-close-popup 
            :disable="!currentCharacter || currentCharacter.length !== 1" 
            @click="addToRecentCharacters(currentCharacter)" />
        </q-card-actions>
      </q-card>
    </q-dialog>
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
  (e: 'annotationStatusChange', status: 'completed' | 'incomplete'): void
}>()

// Component refs
const container = ref<HTMLElement | null>(null)
const isDrawing = ref(false)
const zoomLevel = ref(1)
const selectedAnnotation = ref<any>(null)
const annotations = ref<any[]>([])
const lastSavedAnnotations = ref<string>('')

// Character annotation
const currentCharacter = ref<string>('A')
const recentCharacters = ref<string[]>(['A', 'B', 'C', '1', '2', '3'])
const showCharacterSelector = ref(false)

// Common character sets
const commonCharacterSets = {
  digits: '0123456789'.split(''),
  letters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
  punctuation: ',.?!;:\'"-+*/=()[]{}#@&%$'.split('')
}

// OpenSeadragon and Annotorious instances
let viewer: any = null
let anno: any = null

// Compute if there are any annotations
const hasAnnotations = computed(() => annotations.value.length > 0)

// Add to recent characters
const addToRecentCharacters = (char: string) => {
  if (!char || char.length !== 1) return
  
  // Remove if already exists
  const index = recentCharacters.value.indexOf(char)
  if (index !== -1) {
    recentCharacters.value.splice(index, 1)
  }
  
  // Add to beginning
  recentCharacters.value.unshift(char)
  
  // Keep only the most recent 8
  if (recentCharacters.value.length > 8) {
    recentCharacters.value = recentCharacters.value.slice(0, 8)
  }
  
  // Save to local storage
  localStorage.setItem('ocr-recent-characters', JSON.stringify(recentCharacters.value))
}

// Select a character from the character selector
const selectCharacter = (char: string) => {
  currentCharacter.value = char
  addToRecentCharacters(char)
}

// Format annotation bounds for display
const formatBounds = (annotation: any) => {
  if (!annotation?.selector?.geometry) return ''
  
  const g = annotation.selector.geometry
  if (g.x && g.y && g.width && g.height) {
    return `x:${Math.round(g.x)}, y:${Math.round(g.y)}, w:${Math.round(g.width)}, h:${Math.round(g.height)}`
  }
  return ''
}

// Improved annotation label getter
const getAnnotationLabel = (annotation: any) => {
  if (!annotation) return '?'
  
  // Check various places where the label might be
  if (annotation.body && annotation.body.length > 0) {
    return annotation.body[0].value || '?'
  }
  
  // Try to get from the target properties if present
  if (annotation.target && annotation.target.properties && annotation.target.properties.label) {
    return annotation.target.properties.label
  }
  
  // Otherwise return the placeholder
  return '?'
}

// Initialize the viewer and annotator
onMounted(() => {
  // Load recent characters from localStorage
  const savedRecent = localStorage.getItem('ocr-recent-characters')
  if (savedRecent) {
    try {
      recentCharacters.value = JSON.parse(savedRecent)
    } catch (e) {
      console.error('Failed to parse recent characters:', e)
    }
  }
  
  nextTick(() => {
    initializeViewer()
  })
})

// Clean up on unmount
onUnmounted(() => {
  if (anno) {
    anno.destroy()
    anno = null
  }

  if (viewer) {
    viewer.destroy()
    viewer = null
  }
})

// Initialize the OpenSeadragon viewer and Annotorious
const initializeViewer = () => {
  if (!container.value) return

  // Clean up previous instances
  if (anno) {
    anno.destroy()
    anno = null
  }

  if (viewer) {
    viewer.destroy()
    viewer = null
  }

  // Initialize OpenSeadragon viewer
  viewer = OpenSeadragon({
    element: container.value,
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

  // Initialize Annotorious
  anno = createOSDAnnotator(viewer, {
    style: (annotation: any) => {
      return { 
        stroke: '#3498db',
        strokeWidth: 2,
        fill: 'rgba(52, 152, 219, 0.2)'
      }
    }
  })

  // Load existing annotations
  loadAnnotations()
  
  // Setup event handlers
  setupAnnotationHandlers()
  setupAutoSave()
  
  // Update zoom level when it changes
  viewer.addHandler('zoom', () => {
    if (viewer && viewer.viewport) {
      zoomLevel.value = viewer.viewport.getZoom()
    }
  })
}

// Setup annotation event handlers
const setupAnnotationHandlers = () => {
  console.log('Setting up annotation handlers')
  
  // Use selectionChanged event instead of separate select/deselect events
  anno.on('selectionChanged', (selected: any) => {
    console.log('Selection changed:', selected)
    selectedAnnotation.value = selected?.[0] || null
    
    // Force reactivity update and log
    nextTick(() => {
      console.log('Selected annotation state updated:', selectedAnnotation.value !== null)
    })
    
    // If drawing while selecting, cancel drawing
    if (isDrawing.value && selectedAnnotation.value) {
      isDrawing.value = false
      anno.setDrawingEnabled(false)
    }
  })
  
  // Keep other handlers (createAnnotation, updateAnnotation, etc.)
  anno.on('createAnnotation', (annotation: any) => {
    console.log('Annotation created:', annotation)
    
    // Add the character label to the annotation
    if (!annotation.body || annotation.body.length === 0) {
      annotation.body = [{
        type: 'TextualBody',
        purpose: 'tagging',
        value: currentCharacter.value
      }]
      
      // Update the annotation in Annotorious
      anno.updateAnnotation(annotation)
    }
    
    // Add annotation to our array
    annotations.value.push(annotation)
    emit('update:annotations', annotations.value)
    
    // Add character to recent list
    addToRecentCharacters(currentCharacter.value)
  })
  
  // Log annotation removal
  anno.on('deleteAnnotation', (annotation: any) => {
    console.log('Annotation deleted:', annotation)
    
    // Update our array
    annotations.value = annotations.value.filter(a => a.id !== annotation.id)
    emit('update:annotations', annotations.value)
    
    // Clear selection if this was the selected one
    if (selectedAnnotation.value?.id === annotation.id) {
      selectedAnnotation.value = null
    }
  })
  
  // Update annotations when edited
  anno.on('updateAnnotation', (annotation: any, previous: any) => {
    console.log('Annotation updated:', annotation)
    // Find and replace the updated annotation
    const index = annotations.value.findIndex(a => a.id === previous.id)
    if (index !== -1) {
      annotations.value[index] = annotation
      emit('update:annotations', annotations.value)
    }
    
    // Make sure the annotation has a character label
    if (!annotation.body || !annotation.body.length || !annotation.body[0].value) {
      annotation.body = [{
        type: 'TextualBody',
        purpose: 'tagging',
        value: currentCharacter.value
      }]
      
      // Update the annotation in Annotorious
      anno.updateAnnotation(annotation)
    }
  })
  
  // Add character when creating a new annotation
  anno.on('startDrawing', () => {
    isDrawing.value = true
  })
  
  anno.on('cancelSelected', () => {
    isDrawing.value = false
  })
  
  anno.on('finishDrawing', (annotation: any) => {
    isDrawing.value = false
    
    // Set the character as the annotation body
    if (annotation && currentCharacter.value) {
      anno.updateSelected({
        ...annotation,
        body: [{
          type: 'TextualBody',
          purpose: 'ocr',
          value: currentCharacter.value
        }]
      })
    }
  })
}

// Add auto-save on annotation changes like in TextRegionAnnotator
// This should be placed after the setupAnnotationHandlers function
const setupAutoSave = () => {
  // Watch for annotation changes to trigger save
  watch(annotations, async (newAnnotations, oldAnnotations) => {
    // Skip initial load
    if (oldAnnotations.length === 0 && lastSavedAnnotations.value === '') return
    
    // Check if actual changes were made
    const currentAnnotationsJson = JSON.stringify(newAnnotations)
    if (currentAnnotationsJson !== lastSavedAnnotations.value) {
      console.log('Annotations changed, triggering auto-save')
      await saveAnnotations()
    }
  }, { deep: true })
}

// Load annotations from the server
const loadAnnotations = async () => {
  try {
    console.log('Loading annotations for image:', props.imageId)
    
    // Clear any existing annotations
    if (anno) {
      anno.clearAnnotations()
      annotations.value = []
    }
    
    // Fetch annotations from the server
    const result = await annotationService.getImageAnnotation(props.imageId)
    
    if (result && result.annotations) {
      console.log('Loaded annotations:', result.annotations)
      annotations.value = result.annotations
      
      // Update the annotator
      if (anno) {
        anno.setAnnotations(result.annotations)
      }
      
      // Save as last saved state
      lastSavedAnnotations.value = JSON.stringify(result.annotations)
      
      // Update annotation status
      if (annotations.value.length > 0) {
        emit('annotationStatusChange', 'completed')
      } else {
        emit('annotationStatusChange', 'incomplete')
      }
    }
  } catch (error) {
    console.error('Error loading annotations:', error)
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
    console.log('Saving annotations:', annotations.value)
    
    // Save to backend
    await annotationService.saveAnnotation(props.imageId, {
      annotations: annotations.value
    })
    
    // Update last saved hash to detect future changes
    lastSavedAnnotations.value = JSON.stringify(annotations.value)
    
    // Set annotation status
    if (annotations.value.length > 0) {
      emit('annotationStatusChange', 'completed')
    } else {
      emit('annotationStatusChange', 'incomplete')
    }
    
    // Notify success
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

// Activate drawing tool for rectangle annotations
const activateDrawingTool = () => {
  if (isDrawing.value) {
    anno.cancelSelected()
    isDrawing.value = false
    return
  }
  
  // Make sure a character is selected
  if (!currentCharacter.value || currentCharacter.value.length !== 1) {
    $q.notify({
      type: 'warning',
      message: t('annotator.ocr.selectCharFirst'),
      position: 'top'
    })
    showCharacterSelector.value = true
    return
  }
  
  // Now set the drawing tool
  anno.setDrawingTool('rectangle')
  anno.setDrawingEnabled(true)
  isDrawing.value = true
}

// Cancel drawing
const cancelDrawing = () => {
  if (isDrawing.value) {
    anno.setDrawingEnabled(false)
    isDrawing.value = false
  }
}

// Update the deleteSelected function to match TextRegionAnnotator's approach
const deleteSelected = async () => {
  console.log('Delete selected called, selected annotation:', selectedAnnotation.value)
  
  if (!selectedAnnotation.value) {
    console.warn('No annotation selected to delete')
    return
  }
  
  try {
    const annotationId = selectedAnnotation.value.id
    console.log('Attempting to delete annotation with ID:', annotationId)
    
    // Simply remove the annotation directly - no deselectAll needed
    anno.removeAnnotation(selectedAnnotation.value)
    console.log('Successfully called removeAnnotation')
    
    // The selectionChanged event will automatically clear selectedAnnotation
    // but we'll update our array manually for immediate UI response
    annotations.value = annotations.value.filter(a => a.id !== annotationId)
    
    // Notify about changes
    emit('update:annotations', annotations.value)
    
    // Update annotation status
    if (annotations.value.length === 0) {
      emit('annotationStatusChange', 'incomplete')
    }
    
    console.log('Annotation deletion complete, remaining annotations:', annotations.value.length)
  } catch (error) {
    console.error('Error deleting annotation:', error)
    $q.notify({
      type: 'negative',
      message: t('annotator.notifications.deleteFailed'),
      position: 'top'
    })
  }
}

// Also update the sidebar deletion method to match this pattern
const deleteAnnotation = async (annotationId: string) => {
  console.log('Delete annotation by ID called:', annotationId)
  
  try {
    // Find the annotation by ID
    const annotation = annotations.value.find(a => a.id === annotationId)
    if (!annotation) {
      console.warn('Annotation not found with ID:', annotationId)
      return
    }
    
    // Simply remove the annotation directly
    anno.removeAnnotation(annotation)
    
    // Update our state
    annotations.value = annotations.value.filter(a => a.id !== annotationId)
    
    // Notify about changes
    emit('update:annotations', annotations.value)
    
    // Update annotation status
    if (annotations.value.length === 0) {
      emit('annotationStatusChange', 'incomplete')
    }
    
    console.log('Annotation deleted successfully')
  } catch (error) {
    console.error('Failed to delete annotation:', error)
    $q.notify({
      type: 'negative',
      message: t('annotator.notifications.deleteFailed'),
      position: 'top'
    })
  }
}

// Select annotation by ID
const selectAnnotationById = (annotationId: string) => {
  anno.selectAnnotation({ id: annotationId })
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

// Fix the annotation status watch to properly emit events
watch(annotations, (newAnnotations) => {
  // Check annotation status and emit appropriate events
  if (newAnnotations.length > 0) {
    emit('annotationStatusChange', 'completed')
  } else {
    emit('annotationStatusChange', 'incomplete')
  }
})
</script>

<style lang="scss" scoped>
.ocr-annotator-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #2b2b2b;
  border-radius: 8px;
  overflow: hidden;
  display: grid;
  grid-template-rows: 1fr;
  grid-template-columns: 1fr 240px;
  grid-template-areas: 
    "viewer sidebar";
}

.osd-container {
  grid-area: viewer;
  width: 100%;
  height: 100%;
  position: relative;
}

.annotation-list {
  grid-area: sidebar;
  background: rgba(30, 30, 30, 0.9);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.controls-panel {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  background: rgba(43, 43, 43, 0.8);
  padding: 4px 4px;
  border-radius: 8px;
  color: #fff;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.character-panel {
  position: absolute;
  bottom: 10px;
  left: 10px;
  z-index: 10;
  background: rgba(43, 43, 43, 0.8);
  padding: 8px 10px;
  border-radius: 8px;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  min-width: 200px;
}

.character-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.character-input {
  width: 50px;
  margin-left: 8px;
}

.recent-characters {
  margin-top: 8px;
}

.character-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  
  .q-chip {
    min-width: 28px;
    justify-content: center;
  }
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

.character-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 4px;
}

.character-button {
  width: 30px;
  height: 30px;
  min-height: 30px;
  padding: 0;
  border-radius: 4px;
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
</style> 