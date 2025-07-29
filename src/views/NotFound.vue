<template>
  <q-page class="not-found-page q-pa-md">
    <div class="row items-center justify-center" style="height: 100vh">
      <div class="text-center">
        <q-icon name="error_outline" size="100px" color="negative" />
        <div class="text-h4 q-mt-md">404</div>
        <div class="text-subtitle1 q-mt-sm">{{ t('notFound.message') }}</div>
        <q-btn
          color="primary"
          icon="home"
          :label="t('notFound.backToHome')"
          to="/"
          class="q-mt-lg"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<style lang="scss" scoped>
.not-found-page {
  background: var(--dark-page);
}
</style>