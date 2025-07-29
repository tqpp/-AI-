<template>
  <q-list>
    <q-item
      v-for="route in routes"
      :key="route.path"
      :to="route.path"
      clickable
      v-ripple
      exact
      active-class="q-item--active"
    >
      <q-item-section avatar>
        <q-icon :name="route.meta.icon" size="24px" />
      </q-item-section>
      <q-item-section>
        {{ route.meta.title }}
      </q-item-section>
    </q-item>
  </q-list>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 获取路由配置中的主要导航项
const routes = computed(() => {
  return router.options.routes.filter(route => {
    // 过滤掉重定向和404页面
    return route.meta && route.meta.icon && route.name !== 'NotFound'
  })
})
</script>

<style lang="scss" scoped>
.industrial-nav-menu {
  padding: 8px;
  
  .nav-item {
    transition: all 0.3s ease;
    border-radius: 8px;
    margin-bottom: 4px;
    padding: 8px 4px;
    
    .nav-item-content {
      display: flex;
      width: 100%;
    }
    
    .icon-container {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 8px;
      background: linear-gradient(145deg, #2D3238, #3A3F45);
      box-shadow: 
        inset 0 1px 1px rgba(255,255,255,0.1),
        0 1px 2px rgba(0,0,0,0.2);
    }
    
    .q-icon {
      color: var(--industrial-blue);
    }
    
    &:hover {
      background: rgba(255, 255, 255, 0.05);
      
      .icon-container {
        background: linear-gradient(145deg, #3A3F45, #4A4E54);
      }
    }
    
    &.q-item--active {
      background: rgba(42, 92, 170, 0.15);
      border-left: 3px solid var(--industrial-blue);
      
      .icon-container {
        background: var(--industrial-blue);
      }
      
      .q-icon {
        color: white;
      }
    }
  }
}
</style>