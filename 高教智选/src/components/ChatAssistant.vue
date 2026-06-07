<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1>🎓 智能学习助手</h1>
      <p>让优质教育触手可及</p>
    </div>

    <div class="chat-messages" ref="chatMessages">
      <div v-if="messages.length === 0" class="welcome-message">
        <h3>欢迎使用智能助手</h3>
        <p>我是您的智能学习助手，核心使命是"让优质教育触手可及"</p>
        <ul>
          <li>📚 整合全国优质教育资源，推动高等教育数字化转型</li>
          <li>🏛️ 汇聚清华大学、北京大学、复旦大学等顶尖高校精品课程</li>
          <li>🎯 覆盖理学、工学、文学、管理学等多学科领域</li>
          <li>💡 为师生提供学习路径建议，提升教育质量和公平性</li>
        </ul>
        <p style="margin-top: 20px; font-size: 14px; opacity: 0.7;">请输入您的问题开始对话</p>
      </div>

      <div v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
        <div class="avatar">{{ message.role === 'user' ? (currentUser?.avatar || '👶') : '🧐' }}</div>
        <div class="message-content">
          <p>{{ message.content }}</p>
          <span class="message-time">{{ message.role === 'user' ? '我' : '智能助手' }} · {{ message.time }}</span>
        </div>
      </div>

      <div v-if="isTyping" class="message assistant typing-indicator">
        <div class="avatar">🧐</div>
        <div class="typing-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <div class="chat-input-row">
        <input 
          v-model="inputMessage" 
          type="text" 
          class="chat-input" 
          placeholder="请输入您想了解的课程或问题..."
          @keypress="handleKeyPress"
        />
        <button class="clear-btn" @click="clearChat" :disabled="messages.length === 0">清空</button>
        <button class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim() || isTyping">发送</button>
      </div>
      <p class="disclaimer">⚠️ AI针对课程推荐回答存在一定幻觉，建议于课程列表中查询</p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const messages = ref([])
const inputMessage = ref('')
const isTyping = ref(false)
const chatMessages = ref(null)
const currentUser = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (chatMessages.value) {
    chatMessages.value.scrollTop = chatMessages.value.scrollHeight
  }
}

const loadUser = () => {
  const userData = localStorage.getItem('currentUser')
  if (userData) {
    currentUser.value = JSON.parse(userData)
  }
}

const loadChatHistory = async () => {
  if (!currentUser.value) return
  
  try {
    const response = await axios.get(`/api/chat_history?username=${encodeURIComponent(currentUser.value.username)}`)
    if (response.data.success && response.data.history && response.data.history.length > 0) {
      messages.value = response.data.history.map(item => ({
        role: item.role,
        content: item.content,
        time: item.created_at ? new Date(item.created_at).toLocaleTimeString() : new Date().toLocaleTimeString()
      }))
    }
  } catch (error) {
    console.error('加载聊天历史失败:', error)
  }
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isTyping.value) return

  messages.value.push({
    role: 'user',
    content: message,
    time: new Date().toLocaleTimeString()
  })
  inputMessage.value = ''
  isTyping.value = true

  await scrollToBottom()

  try {
    const response = await axios.post('/api/chat', { 
      message,
      username: currentUser.value?.username || 'anonymous'
    })
    
    if (response.data.success) {
      messages.value.push({
        role: 'assistant',
        content: response.data.response,
        time: new Date().toLocaleTimeString()
      })
    } else {
      messages.value.push({
        role: 'assistant',
        content: `抱歉，出现错误：${response.data.error}`,
        time: new Date().toLocaleTimeString()
      })
    }
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: '网络错误，请稍后重试',
      time: new Date().toLocaleTimeString()
    })
  } finally {
    isTyping.value = false
    await scrollToBottom()
  }
}

const handleKeyPress = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const clearChat = async () => {
  if (!currentUser.value) return
  
  try {
    await axios.post('/api/clear_chat', { username: currentUser.value.username })
    messages.value = []
  } catch (error) {
    console.error('清空失败:', error)
  }
}

onMounted(() => {
  loadUser()
  if (currentUser.value) {
    loadChatHistory()
  }
  window.addEventListener('storage', loadUser)
  window.addEventListener('userUpdated', loadUser)
})

onUnmounted(() => {
  window.removeEventListener('storage', loadUser)
  window.removeEventListener('userUpdated', loadUser)
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 40px);
  background: #f8f9fa;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  text-align: center;
  color: white;
  flex-shrink: 0;
  position: relative;
  z-index: 100;
}

.chat-header h1 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 4px;
}

.chat-header p {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
  position: relative;
  z-index: 1;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message.assistant {
  flex-direction: row;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 20px;
}

.user .avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.assistant .avatar {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
}

.message-content {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 18px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 6px;
}

.assistant .message-content {
  border-bottom-left-radius: 6px;
}

.message-content p {
  margin: 0 0 8px 0;
  line-height: 1.6;
  word-break: break-word;
}

.message-time {
  font-size: 12px;
  opacity: 0.6;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.welcome-message h3 {
  color: #667eea;
  margin-bottom: 10px;
}

.welcome-message ul {
  text-align: left;
  margin-top: 20px;
  padding-left: 20px;
}

.welcome-message li {
  margin-bottom: 8px;
}

.typing-indicator {
  align-items: flex-start;
}

.typing-dots {
  display: flex;
  gap: 6px;
  padding: 12px 16px;
  background: white;
  border-radius: 18px;
  border-bottom-left-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.typing-dots .dot {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input-area {
  padding: 15px 20px;
  background: white;
  border-top: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
  position: relative;
  z-index: 100;
}

.chat-input-row {
  display: flex;
  gap: 12px;
}

.disclaimer {
  font-size: 10px;
  color: #6c757d;
  margin: 0;
  padding-top: 5px;
  border-top: 1px solid #f1f1f1;
}

.chat-input {
  flex: 1;
  padding: 14px 20px;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.3s;
}

.chat-input:focus {
  border-color: #667eea;
}

.send-btn, .clear-btn {
  padding: 14px 24px;
  border: none;
  border-radius: 25px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.send-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.clear-btn {
  background: #f8f9fa;
  color: #6c757d;
}

.clear-btn:hover:not(:disabled) {
  background: #e9ecef;
}

.clear-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>