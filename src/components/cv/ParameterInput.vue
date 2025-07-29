<template>
  <div class="col-12 col-sm-6">
    <q-input 
      v-model="param.name" 
      dense 
      outlined 
      :label="t('cv.parameter.name')"
      :rules="[val => !!val || t('cv.parameter.nameRequired')]"
    />
  </div>
  <div class="col-12 col-sm-6">
    <q-select 
      v-model="param.type" 
      :options="paramTypeOptions" 
      dense 
      outlined 
      :label="t('cv.parameter.type')"
      :rules="[val => !!val || t('cv.parameter.typeRequired')]"
      emit-value
      map-options
      options-dense
    >
      <template v-slot:option="{ itemProps, opt }">
        <q-item v-bind="itemProps">
          <q-item-section avatar>
            <q-icon :name="opt.icon" />
          </q-item-section>
          <q-item-section>
            {{ opt.label }}
          </q-item-section>
        </q-item>
      </template>
    </q-select>
  </div>
  <div class="col-12">
    <q-input 
      v-model="param.description" 
      dense 
      outlined 
      :label="t('cv.parameter.description')"
    />
  </div>
  <div class="col-grow">
    <q-input 
      v-model="param.default" 
      dense 
      outlined 
      :label="t('cv.parameter.defaultValue')"
    />
  </div>
  <div class="col-auto">
    <q-checkbox v-model="param.required" :label="t('cv.parameter.required')" />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  param: {
    type: Object,
    required: true
  },
  paramTypeOptions: {
    type: Array,
    required: true
  }
})
</script>
