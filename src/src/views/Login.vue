<template>
  <div class="login-container">
    <h2>智能家居系统登录</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label>用户名：</label>
        <input v-model="form.username" type="text" required />
      </div>
      <div class="form-group">
        <label>密码：</label>
        <input v-model="form.password" type="password" required />
      </div>
      <button type="submit" class="login-btn">登录</button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const store = useStore()
    const router = useRouter()
    const form = ref({
      username: '',
      password: ''
    })
    const errorMessage = ref('')

    const handleLogin = async () => {
      try {
        const success = await store.dispatch('login', form.value)
        if (success) {
          router.push('/')
        } else {
          errorMessage.value = '用户名或密码错误'
        }
      } catch (error) {
        errorMessage.value = '登录失败，请稍后再试'
      }
    }

    return { form, handleLogin, errorMessage }
  }
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
}

input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.login-btn {
  width: 100%;
  padding: 1rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background-color: #3aa876;
}

.error {
  color: #ff4444;
  margin-top: 1rem;
  text-align: center;
}
</style>