import { createRouter, createWebHashHistory } from 'vue-router'
import i18n from '../i18n/index'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: i18n.global.t('routes.dashboard'), icon: 'dashboard' }
  },
    {
    path: '/annotation',
    name: 'Annotation',
    component: () => import('../views/Annotation.vue'),
    meta: { title: i18n.global.t('routes.annotation'), icon: 'edit' }
  },
  {
    path: '/model',
    name: 'Model',
    component: () => import('../views/Model.vue'),
    meta: { title: i18n.global.t('routes.model'), icon: 'model_training' }
  },
  {
    path: '/model/test/:id',
    name: 'ModelTest',
    component: () => import('../views/Model.vue'),
    props: route => ({
      mode: 'test',
      modelId: parseInt(route.params.id)
    }),
    meta: { title: i18n.global.t('routes.modelTest'), parent: 'Model' }
  },
  {
    path: '/realtime',
    name: 'Realtime',
    component: () => import('../views/Realtime.vue'),
    meta: { title: i18n.global.t('routes.realtime'), icon: 'monitor' }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue'),
    meta: { title: i18n.global.t('routes.history'), icon: 'history' }
  },
  {
    path: '/cv-operations',
    name: 'CVOperations',
    component: () => import('../views/CVOperation.vue'),
    meta: { title: i18n.global.t('routes.cvOperations'), icon: 'science' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { title: i18n.global.t('routes.settings'), icon: 'settings' }
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: i18n.global.t('routes.notFound') }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router