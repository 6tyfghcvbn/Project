<template>
  <div class="settings-container">
    <div class="settings-header">
      <h2>
        <button class="header-avatar-btn" @click="openAvatarPicker">
          <span class="header-avatar">{{ currentUser.avatar || '👶' }}</span>
        </button>
        用户设置
      </h2>
      <p>管理您的账户信息</p>
    </div>

    <div class="settings-content">
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>📝 修改用户名</span>
          </div>
        </template>
        <el-form :model="usernameForm" :rules="usernameRules" ref="usernameFormRef" label-width="100px">
          <el-form-item label="当前用户名">
            <el-input v-model="currentUser.username" disabled />
          </el-form-item>
          <el-form-item label="新用户名" prop="newUsername">
            <el-input v-model="usernameForm.newUsername" placeholder="请输入新用户名" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleUpdateUsername" :loading="usernameLoading">
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>🔐 修改密码</span>
          </div>
        </template>
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
          <el-form-item label="当前密码" prop="currentPassword">
            <el-input 
              v-model="passwordForm.currentPassword" 
              type="password" 
              placeholder="请输入当前密码"
              show-password
            />
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input 
              v-model="passwordForm.newPassword" 
              type="password" 
              placeholder="请输入新密码"
              show-password
            />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input 
              v-model="passwordForm.confirmPassword" 
              type="password" 
              placeholder="请再次输入新密码"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleUpdatePassword" :loading="passwordLoading">
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>📧 修改邮箱</span>
          </div>
        </template>
        <el-form :model="emailForm" :rules="emailRules" ref="emailFormRef" label-width="100px">
          <el-form-item label="当前邮箱">
            <el-input v-model="currentUser.email" disabled />
          </el-form-item>
          <el-form-item label="新邮箱" prop="newEmail">
            <el-input v-model="emailForm.newEmail" placeholder="请输入新邮箱" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleUpdateEmail" :loading="emailLoading">
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const currentUser = ref({ username: '', email: '', avatar: '👶' })

onMounted(() => {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
})

const usernameFormRef = ref(null)
const passwordFormRef = ref(null)
const emailFormRef = ref(null)
const usernameLoading = ref(false)
const passwordLoading = ref(false)
const emailLoading = ref(false)

const openAvatarPicker = () => {
  router.push('/avatar-settings')
}

const usernameForm = reactive({
  newUsername: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const emailForm = reactive({
  newEmail: ''
})

const usernameRules = {
  newUsername: [
    { required: true, message: '请输入新用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ]
}

const validateEmail = (rule, value, callback) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else {
    callback()
  }
}

const emailRules = {
  newEmail: [
    { required: true, message: '请输入新邮箱', trigger: 'blur' },
    { validator: validateEmail, trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleUpdateUsername = async () => {
  if (!usernameFormRef.value) return
  
  await usernameFormRef.value.validate(async (valid) => {
    if (valid) {
      usernameLoading.value = true
      try {
        const response = await axios.put('/api/user/username', {
          userId: currentUser.value.id,
          newUsername: usernameForm.newUsername
        })
        
        if (response.data.success) {
          const updatedUser = { ...currentUser.value, username: usernameForm.newUsername }
          localStorage.setItem('currentUser', JSON.stringify(updatedUser))
          ElMessage.success('用户名修改成功')
          usernameForm.newUsername = ''
          setTimeout(() => {
            window.location.reload()
          }, 1000)
        } else {
          ElMessage.error(response.data.error || '修改失败')
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '网络错误')
      } finally {
        usernameLoading.value = false
      }
    }
  })
}

const handleUpdatePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      passwordLoading.value = true
      try {
        const response = await axios.put('/api/user/password', {
          userId: currentUser.value.id,
          currentPassword: passwordForm.currentPassword,
          newPassword: passwordForm.newPassword
        })
        
        if (response.data.success) {
          ElMessage.success('密码修改成功')
          passwordForm.currentPassword = ''
          passwordForm.newPassword = ''
          passwordForm.confirmPassword = ''
        } else {
          ElMessage.error(response.data.error || '修改失败')
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '网络错误')
      } finally {
        passwordLoading.value = false
      }
    }
  })
}

const handleUpdateEmail = async () => {
  if (!emailFormRef.value) return
  
  await emailFormRef.value.validate(async (valid) => {
    if (valid) {
      emailLoading.value = true
      try {
        const response = await axios.put('/api/user/email', {
          userId: currentUser.value.id,
          newEmail: emailForm.newEmail
        })
        
        if (response.data.success) {
          const updatedUser = { ...currentUser.value, email: emailForm.newEmail }
          localStorage.setItem('currentUser', JSON.stringify(updatedUser))
          ElMessage.success('邮箱修改成功')
          emailForm.newEmail = ''
          setTimeout(() => {
            window.location.reload()
          }, 1000)
        } else {
          ElMessage.error(response.data.error || '修改失败')
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '网络错误')
      } finally {
        emailLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
.settings-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.settings-header {
  margin-bottom: 30px;
}

.settings-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.settings-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.header-avatar {
  font-size: 36px;
}

.header-avatar-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  margin-right: 12px;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-avatar-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: scale(1.1);
}

.header-avatar-btn:focus {
  outline: none;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.settings-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 20px;
}

.settings-card :deep(.el-card__body) {
  padding: 24px;
}

.settings-card :deep(.el-form-item) {
  margin-bottom: 20px;
}

.settings-card :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  padding: 10px 24px;
}

.settings-card :deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.settings-card :deep(.el-input__wrapper) {
  border-radius: 8px;
}
</style>