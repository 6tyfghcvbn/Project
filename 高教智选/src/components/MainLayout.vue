<template>
  <el-container class="app-container">
    <el-aside width="200px" class="fixed-sidebar">
      <el-menu :default-active="activeMenu" class="el-menu-vertical-demo" mode="vertical" router>
        <el-menu-item index="/home">
          <el-icon name="Home" />
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/courses">
          <el-icon name="Menu" />
          <span>课程列表</span>
        </el-menu-item>
        <el-menu-item index="/chart">
          <el-icon name="PieChart" />
          <span>数据可视化</span>
        </el-menu-item>
        <el-menu-item index="/assistant">
          <el-icon name="Message" />
          <span>智能助手</span>
        </el-menu-item>
      </el-menu>
      
      <div class="user-info">
        <button class="user-avatar-btn" @click="goToSettings">
          <span class="avatar-icon">{{ currentUser?.avatar || '👶' }}</span>
          <span class="username">{{ currentUser?.username || '用户' }}</span>
        </button>
        <button class="logout-btn-sidebar" @click="handleLogout">
          <span>退出登录</span>
        </button>
      </div>
    </el-aside>
    
    <el-container class="main-content">
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const currentUser = ref(null)

const loadUser = () => {
  const saved = localStorage.getItem('currentUser')
  currentUser.value = saved ? JSON.parse(saved) : null
}

const handleUserUpdated = () => {
  loadUser()
}

onMounted(() => {
  loadUser()
  window.addEventListener('storage', loadUser)
  window.addEventListener('userUpdated', handleUserUpdated)
})

onUnmounted(() => {
  window.removeEventListener('storage', loadUser)
  window.removeEventListener('userUpdated', handleUserUpdated)
})

const activeMenu = computed(() => {
  return route.name || 'courses'
})

router.beforeEach((to, from, next) => {
  if (!to.name) {
    next({ name: 'home' })
  } else {
    next()
  }
})

const goToSettings = () => {
  router.push('/settings')
}

const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    localStorage.removeItem('currentUser')
    ElMessage.success('退出成功')
    setTimeout(() => {
      window.location.reload()
    }, 1000)
  }).catch(() => {
    ElMessage.info('已取消退出')
  })
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.fixed-sidebar {
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.el-menu-vertical-demo {
  flex: 1;
  overflow-y: auto;
}

.user-info {
  padding: 16px;
  border-top: none;
  background: transparent;
}

.user-avatar-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 14px;
  border: none;
  border-radius: 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-avatar-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.avatar-icon {
  font-size: 24px;
}

.username {
  font-size: 14px;
  font-weight: 600;
  flex: 1;
  text-align: left;
}

.logout-btn-sidebar {
  width: 100%;
  margin-top: 12px;
  padding: 8px 14px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  background: transparent;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.logout-btn-sidebar:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.main-content {
  height: 100vh;
  overflow: hidden;
}

.el-main {
  height: 100vh;
  padding: 20px;
  overflow-y: auto;
}
</style>