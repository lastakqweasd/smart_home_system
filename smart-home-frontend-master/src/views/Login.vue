<template>
  <div class="login-container">
    <div class="background-elements">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
    
    <div class="form-card">
      <!-- 顶部Logo和标题 -->
      <div class="form-header">
        <div class="logo-container">
          <div class="logo-icon">
            <i class="fas fa-home"></i>
          </div>
          <h1 class="app-title">Smart Home</h1>
        </div>
        <h2 class="form-title">{{ isLoginMode ? '欢迎回来' : '创建账户' }}</h2>
        <p class="form-subtitle">{{ isLoginMode ? '登录您的智能家居系统' : '注册新的智能家居账户' }}</p>
      </div>
      
      <!-- 登录表单 -->
      <form v-if="isLoginMode" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <div class="input-container">
            <i class="fas fa-user input-icon"></i>
            <input 
              v-model="loginForm.username" 
              type="text" 
              required 
              placeholder="请输入用户名"
              class="form-input"
            />
          </div>
        </div>
        
        <div class="form-group">
          <div class="input-container">
            <i class="fas fa-lock input-icon"></i>
            <input 
              v-model="loginForm.password" 
              :type="showPassword ? 'text' : 'password'"
              required 
              placeholder="请输入密码"
              class="form-input"
            />
            <button 
              type="button" 
              @click="togglePassword" 
              class="password-toggle"
            >
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
        </div>
        
        <button type="submit" class="primary-btn" :disabled="loading">
          <span v-if="loading" class="btn-loading">
            <i class="fas fa-spinner fa-spin"></i>
            登录中...
          </span>
          <span v-else class="btn-content">
            <i class="fas fa-sign-in-alt"></i>
            立即登录
          </span>
        </button>
      </form>

      <!-- 注册表单 -->
      <form v-else @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <div class="input-container">
            <i class="fas fa-user input-icon"></i>
            <input 
              v-model="registerForm.username" 
              type="text" 
              required 
              placeholder="请输入用户名"
              class="form-input"
            />
          </div>
        </div>
        
  <div class="form-group">
  <div class="input-container">
    <i class="fas fa-lock input-icon"></i>
    <input 
      v-model="registerForm.password" 
      :type="showPassword ? 'text' : 'password'"
      required 
      placeholder="至少8位字符，包含大小写和数字"
      minlength="8"
      @input="validatePassword"
      :class="{
        'form-input': true,
        'input-error': passwordError,
        'input-valid': isPasswordValid
      }"
    />
    <button 
      type="button" 
      @click="togglePassword" 
      class="password-toggle"
      :title="showPassword ? '隐藏密码' : '显示密码'"
    >
      <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
    </button>
  </div>

  <!-- 密码强度指示器 -->
  <div class="password-strength" v-if="registerForm.password">
    <div class="strength-bar">
      <div 
        class="strength-fill" 
        :style="{ width: passwordStrength.width }"
        :class="passwordStrength.class"
      ></div>
    </div>
    <span class="strength-text">
      <i :class="passwordStrength.icon"></i>
      {{ passwordStrength.text }}
    </span>
  </div>

  <!-- 实时错误提示 -->
  <transition name="fade">
    <div v-if="passwordError" class="password-error">
      <i class="fas fa-exclamation-circle"></i>
      {{ passwordError }}
    </div>
  </transition>

  <!-- 密码规则提示 -->
  <ul class="password-rules">
    <li :class="{ 'rule-valid': hasMinLength }">
      <i :class="hasMinLength ? 'fas fa-check-circle' : 'far fa-circle'"></i>
      至少8位字符
    </li>
    <li :class="{ 'rule-valid': hasUpperCase }">
      <i :class="hasUpperCase ? 'fas fa-check-circle' : 'far fa-circle'"></i>
      包含大写字母
    </li>
    <li :class="{ 'rule-valid': hasNumber }">
      <i :class="hasNumber ? 'fas fa-check-circle' : 'far fa-circle'"></i>
      包含数字
    </li>
  </ul>
</div>
        
        <div class="form-group">
          <div class="input-container">
            <i class="fas fa-check-circle input-icon"></i>
            <input 
              v-model="registerForm.confirmPassword" 
              :type="showConfirmPassword ? 'text' : 'password'"
              required 
              placeholder="请再次输入密码"
              class="form-input"
              :class="{ 'error': passwordMismatch }"
            />
            <button 
              type="button" 
              @click="toggleConfirmPassword" 
              class="password-toggle"
            >
              <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <div v-if="passwordMismatch" class="field-error">
            <i class="fas fa-exclamation-circle"></i>
            密码不一致
          </div>
        </div>
        
        <button type="submit" class="primary-btn" :disabled="loading || passwordMismatch">
          <span v-if="loading" class="btn-loading">
            <i class="fas fa-spinner fa-spin"></i>
            注册中...
          </span>
          <span v-else class="btn-content">
            <i class="fas fa-user-plus"></i>
            创建账户
          </span>
        </button>
      </form>

      <!-- 消息提示 -->
      <transition name="message-fade">
        <div v-if="errorMessage" class="message error-message">
          <i class="fas fa-exclamation-triangle"></i>
          {{ errorMessage }}
        </div>
      </transition>
      
      <transition name="message-fade">
        <div v-if="successMessage" class="message success-message">
          <i class="fas fa-check-circle"></i>
          {{ successMessage }}
        </div>
      </transition>

      <!-- 切换模式 -->
      <div class="mode-switch">
        <div class="divider">
          <span>或者</span>
        </div>
        
        <button @click="switchMode" class="switch-btn">
          <span v-if="isLoginMode">
            还没有账户？<strong>立即注册</strong>
          </span>
          <span v-else>
            已有账户？<strong>立即登录</strong>
          </span>
        </button>
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
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    
    // 登录表单
    const loginForm = ref({
      username: '',
      password: ''
    })
    
    // 注册表单
    const registerForm = ref({
      username: '',
      email: '',
      phone: '',
      nickname: '',
      password: '',
      confirmPassword: ''
    })
    
    // 状态管理
    const errorMessage = ref('')
    const successMessage = ref('')
    const passwordError = ref('')
    const isPasswordValid = ref(false)
    const loading = computed(() => store.state.loading)

    // 密码规则验证
    const hasMinLength = computed(() => registerForm.value.password.length >= 8)
    const hasUpperCase = computed(() => /[A-Z]/.test(registerForm.value.password))
    const hasNumber = computed(() => /[0-9]/.test(registerForm.value.password))

    // 密码强度计算
    const passwordStrength = computed(() => {
      const pwd = registerForm.value.password
      if (!pwd) return { width: '0%', text: '', class: '', icon: '' }

      let strength = 0
      if (pwd.length >= 8) strength += 1
      if (pwd.length >= 12) strength += 1
      if (/[A-Z]/.test(pwd)) strength += 1
      if (/[a-z]/.test(pwd)) strength += 1
      if (/[0-9]/.test(pwd)) strength += 1
      if (/[^A-Za-z0-9]/.test(pwd)) strength += 1

      if (strength <= 2) {
        return { width: '33%', text: '弱', class: 'weak', icon: 'fas fa-exclamation-triangle' }
      } else if (strength <= 4) {
        return { width: '66%', text: '中', class: 'medium', icon: 'fas fa-check-circle' }
      } else {
        return { width: '100%', text: '强', class: 'strong', icon: 'fas fa-shield-alt' }
      }
    })

    // 密码验证逻辑
    const validatePassword = () => {
      const pwd = registerForm.value.password
      passwordError.value = ''
      isPasswordValid.value = false
      
      if (pwd.length > 0 && pwd.length < 8) {
        passwordError.value = '密码至少需要8位字符'
      } else if (!/[A-Z]/.test(pwd)) {
        passwordError.value = '建议包含至少一个大写字母'
      } else if (!/[0-9]/.test(pwd)) {
        passwordError.value = '建议包含至少一个数字'
      } else {
        isPasswordValid.value = true
      }
    }

    // 密码匹配检查
    const passwordMismatch = computed(() => {
      return registerForm.value.confirmPassword && 
             registerForm.value.password !== registerForm.value.confirmPassword
    })

    // 密码可见性切换
    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    const toggleConfirmPassword = () => {
      showConfirmPassword.value = !showConfirmPassword.value
    }

    // 切换登录/注册模式
    const switchMode = () => {
      isLoginMode.value = !isLoginMode.value
      errorMessage.value = ''
      successMessage.value = ''
      passwordError.value = ''
      showPassword.value = false
      showConfirmPassword.value = false
      loginForm.value = { username: '', password: '' }
      registerForm.value = { username: '', email: '', phone: '', nickname: '', password: '', confirmPassword: '' }
    }

    // 登录处理
    const handleLogin = async () => {
      errorMessage.value = ''
      successMessage.value = ''
      
      try {
        const success = await store.dispatch('login', loginForm.value)
        if ( success) {
          successMessage.value = '登录成功！正在跳转...'
          setTimeout(() => {
            router.push('/')
          }, 1000)
        } else {
          errorMessage.value = '用户名或密码错误，请重试'
        }
      } catch (error) {
        errorMessage.value = '登录失败，请检查网络连接'
        console.error('登录错误:', error)
      }
    }

    // 注册处理
    const handleRegister = async () => {
      errorMessage.value = ''
      successMessage.value = ''
      passwordError.value = ''

      // 前端验证
      if (!hasMinLength.value) {
        errorMessage.value = '密码长度至少8位字符'
        return
      }
      
      if (!hasUpperCase.value) {
        errorMessage.value = '密码必须包含至少一个大写字母'
        return
      }
      
      if (!hasNumber.value) {
        errorMessage.value = '密码必须包含至少一个数字'
        return
      }

      if (passwordMismatch.value) {
        errorMessage.value = '两次输入的密码不一致'
        return
      }

      try {
        const success = await store.dispatch('register', {
          username: registerForm.value.username,
          password: registerForm.value.password,
          password_confirm: registerForm.value.confirmPassword,
          email: registerForm.value.email || null,
          phone: registerForm.value.phone || null,
          nickname: registerForm.value.nickname || registerForm.value.username
        })

        if (success) {
          successMessage.value = '注册成功！正在跳转...'
          setTimeout(() => {
            router.push('/')
          }, 1500)
        } else {
          errorMessage.value = store.state.error || '注册失败，请重试'
        }
      } catch (error) {
        errorMessage.value = error.response?.data?.detail || 
                           error.response?.data?.message || 
                           '注册失败，请检查网络连接'
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
      passwordError,
      isPasswordValid,
      loading,
      showPassword,
      showConfirmPassword,
      togglePassword,
      toggleConfirmPassword,
      passwordStrength,
      passwordMismatch,
      hasMinLength,
      hasUpperCase,
      hasNumber,
      validatePassword
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
  position: relative;
  overflow: hidden;
}

/* 背景装饰元素 */
.background-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: -50px;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: -30px;
  animation-delay: 2s;
}

.circle-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  33% { transform: translateY(-20px) rotate(120deg); }
  66% { transform: translateY(10px) rotate(240deg); }
}

/* 表单卡片 */
.form-card {
  max-width: 450px;
  width: 100%;
  padding: 3rem 2.5rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 1px 1px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 表单头部 */
.form-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 1rem;
}

.logo-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.app-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-title {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
  font-size: 1.75rem;
  font-weight: 700;
}

.form-subtitle {
  margin: 0;
  color: #718096;
  font-size: 0.9rem;
}

/* 表单样式 */
.auth-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  color: #a0aec0;
  font-size: 16px;
  z-index: 2;
  transition: color 0.3s ease;
}

.form-input {
  width: 100%;
  padding: 16px 16px 16px 50px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
  background: #f7fafc;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:focus + .input-icon {
  color: #667eea;
}

.form-input.error {
  border-color: #e53e3e;
  background: #fff5f5;
}

.input-error {
  border-color: #e53e3e !important;
  background-color: #fff5f5;
}

.input-valid {
  border-color: #38a169 !important;
}

.password-toggle {
  position: absolute;
  right: 16px;
  background: none;
  border: none;
  color: #a0aec0;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
  z-index: 2;
}

.password-toggle:hover {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

/* 密码强度指示器 */
.password-strength {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
  border-radius: 2px;
}

.weak {
  background: linear-gradient(90deg, #e53e3e, #f56565);
}

.medium {
  background: linear-gradient(90deg, #ed8936, #f6ad55);
}

.strong {
  background: linear-gradient(90deg, #38a169, #68d391);
}

.strength-text {
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 30px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 错误提示 */
.password-error {
  margin-top: 6px;
  color: #e53e3e;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.field-error {
  margin-top: 6px;
  color: #e53e3e;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 密码规则提示 */
.password-rules {
  margin-top: 8px;
  padding-left: 20px;
  font-size: 0.75rem;
  color: #718096;
  list-style-type: none;
}

.password-rules li {
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.rule-valid {
  color: #38a169;
}

/* 按钮样式 */
.primary-btn {
  width: 100%;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.primary-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.primary-btn:hover:not(:disabled)::before {
  left: 100%;
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-loading,
.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-loading i {
  font-size: 14px;
}

/* 消息提示 */
.message {
  padding: 12px 16px;
  border-radius: 10px;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  font-weight: 500;
}

.error-message {
  background: linear-gradient(135deg, #fed7d7, #feb2b2);
  color: #c53030;
  border: 1px solid #fc8181;
}

.success-message {
  background: linear-gradient(135deg, #c6f6d5, #9ae6b4);
  color: #2f855a;
  border: 1px solid #68d391;
}

/* 过渡动画 */
.message-fade-enter-active,
.message-fade-leave-active,
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.message-fade-enter-from,
.message-fade-leave-to,
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 模式切换 */
.mode-switch {
  margin-top: 2rem;
  text-align: center;
}

.divider {
  position: relative;
  margin: 1.5rem 0;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e2e8f0;
}

.divider span {
  background: rgba(255, 255, 255, 0.95);
  padding: 0 15px;
  color: #a0aec0;
  font-size: 0.85rem;
  position: relative;
}

.switch-btn {
  background: none;
  border: 2px solid #e2e8f0;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  color: #4a5568;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.switch-btn:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
  color: #667eea;
}

.switch-btn strong {
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .form-card {
    padding: 2rem 1.5rem;
    margin: 1rem;
    border-radius: 16px;
  }
  
  .form-title {
    font-size: 1.5rem;
  }
  
  .app-title {
    font-size: 1.25rem;
  }
  
  .logo-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}

@media (max-width: 360px) {
  .form-input {
    padding: 14px 14px 14px 45px;
  }
  
  .input-icon {
    left: 14px;
  }
  
  .password-toggle {
    right: 14px;
  }
}
</style>