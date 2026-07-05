<template>
  <div class="avatar-settings-container">
    <div class="avatar-settings-header">
      <button class="back-btn" @click="goBack">
        <span>←</span>
        <span>返回</span>
      </button>
      <h2>更换头像</h2>
    </div>

    <div class="avatar-content">
      <div class="current-avatar-section">
        <div class="current-avatar">
          <span class="avatar-emoji">{{ currentUser.avatar || '👶' }}</span>
        </div>
        <p class="current-avatar-label">当前头像</p>
      </div>

      <div class="avatar-options-section">
        <h3>选择新头像</h3>
        <div class="custom-avatar-section">
          <div class="custom-avatar-input-wrapper">
            <input 
              type="text" 
              v-model="customAvatar" 
              placeholder="粘贴 emoji 或输入" 
              @paste="handlePaste"
              @keyup.enter="applyCustomAvatar"
              class="custom-avatar-input"
            />
            <button @click="applyCustomAvatar" class="custom-avatar-btn">使用</button>
          </div>
          <p class="custom-avatar-hint">💡 可从 <a href="https://www.emojiall.com/zh-hans/all-emojis" target="_blank">emojiall.com</a> 复制 emoji</p>
        </div>
        <div class="avatar-grid">
          <div 
            v-for="avatar in avatarOptions" 
            :key="avatar"
            class="avatar-item"
            :class="{ active: currentUser.avatar === avatar }"
            @click="selectAvatar(avatar)"
          >
            {{ avatar }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const currentUser = ref({ username: '', email: '', avatar: '👶' })
const customAvatar = ref('')

const avatarOptions = [
  '👶', '👦', '👧', '👨', '👩', '👴', '👵', '🧑',
  '👨‍💼', '👩‍💼', '👨‍🎓', '👩‍🎓', '🤵', '👰',
  '👨‍🔬', '👩‍🔬', '👨‍💻', '👩‍💻', '🎓', '📚',
  '🌟', '⭐', '🔥', '💡', '🎯', '🎨'
]

onMounted(() => {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
})

const goBack = () => {
  router.push('/settings')
}

const isEmoji = (char) => {
  const emojiRegex = /^[\p{Emoji}\p{Emoji_Presentation}\p{Emoji_Modifier}\p{Emoji_Modifier_Base}\p{Emoji_Component}]+$/u
  return emojiRegex.test(char)
}

const handlePaste = (e) => {
  e.preventDefault()
  const text = e.clipboardData.getData('text')
  if (text) {
    customAvatar.value = text.trim()
  }
}

const applyCustomAvatar = () => {
  const avatar = customAvatar.value.trim()
  if (!avatar) {
    ElMessage.warning('请输入或粘贴 emoji')
    return
  }
  if (!isEmoji(avatar)) {
    ElMessage.warning('请输入有效的 emoji')
    return
  }
  selectAvatar(avatar)
  customAvatar.value = ''
}

const selectAvatar = async (avatar) => {
  try {
    const response = await axios.put('/api/user/avatar', {
      userId: currentUser.value.id,
      avatar: avatar
    })
    
    if (response.data.success) {
      currentUser.value.avatar = avatar
      const userData = localStorage.getItem('currentUser')
      if (userData) {
        const user = JSON.parse(userData)
        user.avatar = avatar
        localStorage.setItem('currentUser', JSON.stringify(user))
      }
      window.dispatchEvent(new Event('userUpdated'))
      ElMessage.success('头像更换成功')
    } else {
      ElMessage.error(response.data.error || '头像更换失败')
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
  }
}
</script>

<style scoped>
.avatar-settings-container {
  min-height: 100vh;
  background: #f8fafc;
  padding: 20px;
}

.avatar-settings-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 30px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
  font-size: 14px;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: #f1f5f9;
  color: #334155;
}

.avatar-settings-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.avatar-content {
  max-width: 600px;
  margin: 0 auto;
}

.current-avatar-section {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.current-avatar {
  width: 120px;
  height: 120px;
  margin: 0 auto 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-emoji {
  font-size: 60px;
}

.current-avatar-label {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.avatar-options-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.avatar-options-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 20px;
  text-align: center;
}

.custom-avatar-section {
  margin-bottom: 24px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 10px;
  text-align: center;
}

.custom-avatar-input-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  justify-content: center;
  align-items: center;
}

.custom-avatar-input {
  flex: 1;
  max-width: 200px;
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 24px;
  text-align: center;
  outline: none;
  transition: all 0.2s ease;
  background: white;
}

.custom-avatar-input::placeholder {
  font-size: 14px;
  color: #94a3b8;
}

.custom-avatar-input::-webkit-input-placeholder {
  font-size: 14px;
  color: #94a3b8;
}

.custom-avatar-input::-moz-placeholder {
  font-size: 14px;
  color: #94a3b8;
}

.custom-avatar-input:-ms-input-placeholder {
  font-size: 14px;
  color: #94a3b8;
}

.custom-avatar-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.custom-avatar-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.custom-avatar-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.custom-avatar-hint {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.custom-avatar-hint a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.custom-avatar-hint a:hover {
  text-decoration: underline;
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.avatar-item {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  width: 60px;
  height: 60px;
  margin: 0 auto;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
  background: #f8fafc;
}

.avatar-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: scale(1.1);
}

.avatar-item.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}
</style>