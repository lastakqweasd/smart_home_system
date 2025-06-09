<template>
  <div class="login-container">
    <div class="form-card">
      <h2>{{ isLoginMode ? '智能家居系统登录' : '用户注册' }}</h2>
      
      <!-- 登录表单 -->
      <form v-if="isLoginMode" @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名：</label>
          <input 
            v-model="loginForm.username" 
            type="text" 
            required 
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label>密码：</label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            required 
            placeholder="请输入密码"
          />
        </div>
        <button type="submit" class="primary-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <!-- 注册表单 -->
      <form v-else @submit.prevent="handleRegister">
        <div class="form-group">
          <label>用户名：</label>
          <input 
            v-model="registerForm.username" 
            type="text" 
            required 
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label>密码：</label>
          <input 
            v-model="registerForm.password" 
            type="password" 
            required 
            placeholder="请输入密码"
          />
        </div>
        <div class="form-group">
          <label>确认密码：</label>
          <input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            required 
            placeholder="请再次输入密码"
          />
        </div>
        <button type="submit" class="primary-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <!-- 错误信息 -->
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success">{{ successMessage }}</p>

      <!-- 切换模式 -->
      <div class="mode-switch">
        <p v-if="isLoginMode">
          还没有账户？
          <a @click="switchMode" class="link">立即注册</a>
        </p>
        <p v-else>
          已有账户？
          <a @click="switchMode" class="link">返回登录</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // 表单模式控制
    const isLoginMode = ref(true)
    
    // 登录表单
    const loginForm = ref({
      username: '',
      password: ''
    })
    
    // 注册表单
    const registerForm = ref({
      username: '',
      password: '',
      confirmPassword: ''
    })
    
    // 状态管理
    const errorMessage = ref('')
    const successMessage = ref('')
    const loading = computed(() => store.state.loading)

    // 切换登录/注册模式
    const switchMode = () => {
      isLoginMode.value = !isLoginMode.value
      errorMessage.value = ''
      successMessage.value = ''
      // 清空表单
      loginForm.value = { username: '', password: '' }
      registerForm.value = { username: '', password: '', confirmPassword: '' }
    }

    // 登录处理
    const handleLogin = async () => {
      errorMessage.value = ''
      successMessage.value = ''
      
      try {
        const success = await store.dispatch('login', loginForm.value)
        if (success) {
          successMessage.value = '登录成功，正在跳转...'
          setTimeout(() => {
            router.push('/')
          }, 1000)
        } else {
          errorMessage.value = '用户名或密码错误'
        }
      } catch (error) {
        errorMessage.value = '登录失败，请稍后再试'
        console.error('登录错误:', error)
      }
    }

    // 注册处理
    const handleRegister = async () => {
      errorMessage.value = ''
      successMessage.value = ''

      // 前端验证
      if (registerForm.value.password !== registerForm.value.confirmPassword) {
        errorMessage.value = '两次输入的密码不一致'
        return
      }

      if (registerForm.value.password.length < 6) {
        errorMessage.value = '密码长度至少为6位'
        return
      }

      try {
        const success = await store.dispatch('register', {
          username: registerForm.value.username,
          password: registerForm.value.password
        })

        if (success) {
          successMessage.value = '注册成功，正在跳转...'
          setTimeout(() => {
            router.push('/')
          }, 1500)
        } else {
          // 错误信息从 store 中获取
          errorMessage.value = store.state.error || '注册失败，请重试'
        }
      } catch (error) {
        errorMessage.value = '注册失败，请稍后再试'
        console.error('注册错误:', error)
      }
    }

    return { 
      isLoginMode,
      loginForm, 
      registerForm,
      handleLogin, 
      handleRegister,
      switchMode,
      errorMessage,
      successMessage,
      loading
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.form-card {
  max-width: 400px;
  width: 100%;
  padding: 2.5rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.875rem;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.primary-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #42b983, #3aa876);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.3);
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error {
  color: #ff4757;
  margin: 1rem 0;
  text-align: center;
  padding: 0.75rem;
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 6px;
  font-size: 0.9rem;
}

.success {
  color: #27ae60;
  margin: 1rem 0;
  text-align: center;
  padding: 0.75rem;
  background: #f0fff4;
  border: 1px solid #c6f6d5;
  border-radius: 6px;
  font-size: 0.9rem;
}

.mode-switch {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e1e5e9;
}

.mode-switch p {
  margin: 0;
  color: #666;
}

.link {
  color: #42b983;
  cursor: pointer;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.link:hover {
  color: #3aa876;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .form-card {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  h2 {
    font-size: 1.5rem;
  }
}
</style>