// 指在页面跳转时不会重新加载整个页面，而是只更改局部区域的内容，以提升用户体验和页面加载速度
import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import AddDevice from '../views/AddDevice.vue'
import CreateScene from '../views/CreateScene.vue'
import Login from '../views/Login.vue'
import store from '../store/s_index'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: true }
  },
  {
    path:'/add-device',
    name:'AddDevice',
    component: AddDevice,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  // 创建场景模式
  {
    path: '/create-scene',
    name: 'CreateScene',
    component: CreateScene,
  }
  // 可以添加更多路由，如设备详情页面等
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated
  
  // 需要认证且未登录
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  }
  // 已登录但访问登录页
  else if (to.path === '/login' && isAuthenticated) {
    next('/')
  }
  // 其他情况正常放行
  else {
    next()
  }
})

export default router

