<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo-section">
          <div class="logo-icon">
            <span class="logo-text">📚</span>
          </div>
          <h1 class="app-title">课程管理系统</h1>
          <p class="app-subtitle">探索优质课程，开启学习之旅</p>
        </div>
      </div>
      
      <div class="auth-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'login' }"
          @click="activeTab = 'login'"
        >
          <span class="tab-icon">🔐</span>
          <span>登录</span>
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'register' }"
          @click="activeTab = 'register'"
        >
          <span class="tab-icon">📝</span>
          <span>注册</span>
        </button>
      </div>
      
      <div class="auth-form">
        <template v-if="activeTab === 'login'">
          <h2 class="form-title">欢迎回来</h2>
          <el-form :model="loginForm" ref="loginRef" class="form-content">
            <el-form-item class="form-group">
              <div class="input-wrapper">
                <span class="input-icon">👤</span>
                <el-input 
                  v-model="loginForm.username" 
                  placeholder="请输入用户名" 
                  class="auth-input"
                />
              </div>
            </el-form-item>
            <el-form-item class="form-group">
              <div class="input-wrapper">
                <span class="input-icon">🔑</span>
                <el-input 
                  :type="showLoginPassword ? 'text' : 'password'" 
                  v-model="loginForm.password" 
                  placeholder="请输入密码" 
                  class="auth-input"
                />
                <span class="password-toggle" @click="toggleLoginPassword">
                  {{ showLoginPassword ? '🤪' : '😎' }}
                </span>
              </div>
            </el-form-item>
            <el-form-item class="form-group">
              <el-button type="primary" @click="handleLogin" class="submit-btn">
                <span class="btn-icon">🚀</span>
                <span>登录</span>
              </el-button>
            </el-form-item>
          </el-form>
        </template>
        
        <template v-else>
          <h2 class="form-title">创建账号</h2>
          <el-form :model="registerForm" ref="registerRef" class="form-content">
            <el-form-item class="form-group">
              <div class="input-wrapper">
                <span class="input-icon">👤</span>
                <el-input 
                  v-model="registerForm.username" 
                  placeholder="请输入用户名" 
                  class="auth-input"
                />
              </div>
            </el-form-item>
            <el-form-item class="form-group">
              <div class="input-wrapper">
                <span class="input-icon">📧</span>
                <el-input 
                  v-model="registerForm.email" 
                  placeholder="请输入邮箱" 
                  class="auth-input"
                />
              </div>
            </el-form-item>
            <el-form-item class="form-group">
              <div class="input-wrapper">
                <span class="input-icon">🔑</span>
                <el-input 
                  :type="showRegisterPassword ? 'text' : 'password'" 
                  v-model="registerForm.password" 
                  placeholder="请输入密码" 
                  class="auth-input"
                />
                <span class="password-toggle" @click="toggleRegisterPassword">
                  {{ showRegisterPassword ? '🤪' : '😎' }}
                </span>
              </div>
            </el-form-item>
            <el-form-item class="form-group">
              <div class="input-wrapper">
                <span class="input-icon">🔐</span>
                <el-input 
                  :type="showConfirmPassword ? 'text' : 'password'" 
                  v-model="registerForm.confirmPassword" 
                  placeholder="请再次输入密码" 
                  class="auth-input"
                />
                <span class="password-toggle" @click="toggleConfirmPassword">
                  {{ showConfirmPassword ? '🤪' : '😎' }}
                </span>
              </div>
            </el-form-item>
            <el-form-item class="form-group">
              <el-button type="primary" @click="handleRegister" class="submit-btn">
                <span class="btn-icon">✨</span>
                <span>注册</span>
              </el-button>
            </el-form-item>
          </el-form>
        </template>
      </div>
      
      <div class="auth-footer">
        <p>© 国家高等教育智慧教育平台 | <a href="https://higher.smartedu.cn/" target="_blank" class="footer-link">https://higher.smartedu.cn/</a></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const emit = defineEmits(['login'])

const activeTab = ref('login')

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})

const loginRef = ref(null)
const registerRef = ref(null)

const showLoginPassword = ref(false)
const showRegisterPassword = ref(false)
const showConfirmPassword = ref(false)

const toggleLoginPassword = () => {
  showLoginPassword.value = !showLoginPassword.value
}

const toggleRegisterPassword = () => {
  showRegisterPassword.value = !showRegisterPassword.value
}

const toggleConfirmPassword = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning({
      message: '请填写用户名和密码',
      center: true,
      duration: 3000
    })
    return
  }
  
  try {
    const response = await axios.post('/api/login', {
      username: loginForm.username,
      password: loginForm.password
    })
    
    ElMessage.success({
      message: '登录成功',
      center: true,
      duration: 2000
    })
    
    setTimeout(() => {
      emit('login', response.data)
    }, 1000)
  } catch (error) {
    const errorMsg = error.response?.data?.error || '登录失败'
    ElMessage.error({
      message: errorMsg,
      center: true,
      duration: 3000
    })
  }
}

const handleRegister = async () => {
  if (!registerForm.username || !registerForm.password || !registerForm.email) {
    ElMessage.warning({
      message: '请填写完整信息',
      center: true,
      duration: 3000
    })
    return
  }
  
  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.warning({
      message: '两次输入的密码不一致',
      center: true,
      duration: 3000
    })
    return
  }
  
  try {
    await axios.post('/api/register', {
      username: registerForm.username,
      password: registerForm.password,
      email: registerForm.email
    })
    
    ElMessage.success({
      message: '注册成功，请登录',
      center: true,
      duration: 3000
    })
    
    setTimeout(() => {
      activeTab.value = 'login'
      registerForm.username = ''
      registerForm.password = ''
      registerForm.confirmPassword = ''
      registerForm.email = ''
    }, 1500)
  } catch (error) {
    const errorMsg = error.response?.data?.error || '注册失败'
    ElMessage.error({
      message: errorMsg,
      center: true,
      duration: 3000
    })
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.auth-container::before,
.auth-container::after {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  opacity: 0.3;
  animation: float 10s ease-in-out infinite;
}

.auth-container::before {
  background: rgba(255, 255, 255, 0.2);
  top: -100px;
  left: -100px;
}

.auth-container::after {
  background: rgba(255, 255, 255, 0.15);
  bottom: -100px;
  right: -100px;
  animation-delay: -5s;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -30px) scale(1.1); }
  50% { transform: translate(0, -50px) scale(0.9); }
  75% { transform: translate(-30px, -30px) scale(1.05); }
}

.auth-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.15);
  padding: 40px;
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 10;
  animation: fadeInUp 0.5s ease-out;
  box-sizing: border-box;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
}

.logo-text {
  font-size: 36px;
}

.app-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.app-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.auth-tabs {
  display: flex;
  background: #f1f5f9;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 24px;
  width: 100%;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background: #e2e8f0;
}

.tab-btn.active {
  background: white;
  color: #6366f1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.tab-icon {
  font-size: 16px;
}

.auth-form {
  margin-bottom: 24px;
  width: 100%;
}

.form-title {
  text-align: center;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 20px 0;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.form-group {
  margin: 0;
  padding: 0;
}

.form-content :deep(.el-form) {
  margin: 0;
  padding: 0;
  width: 100%;
}

.form-content :deep(.el-form-item) {
  margin: 0;
  padding: 0;
  width: 100%;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 16px;
  font-size: 18px;
  z-index: 1;
}

.auth-input {
  width: 100%;
  padding: 14px 48px 14px 48px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.3s ease;
  background: #f8fafc;
  box-sizing: border-box;
}

.auth-input:focus {
  outline: none;
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.submit-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
}

.submit-btn:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: 16px;
}

.auth-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.auth-footer p {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.footer-link {
  color: #6366f1;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #8b5cf6;
  text-decoration: underline;
}

.password-toggle {
  position: absolute;
  right: 16px;
  font-size: 18px;
  cursor: pointer;
  z-index: 1;
  transition: transform 0.2s ease;
}

.password-toggle:hover {
  transform: scale(1.1);
}
</style>
