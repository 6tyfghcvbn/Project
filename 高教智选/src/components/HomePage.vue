<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-icon">
          <span>📚</span>
        </div>
        <h1 class="hero-title">
          <a href="https://higher.smartedu.cn/" target="_blank">国家高等教育智慧教育平台</a>
        </h1>
        <p class="hero-description">
          汇聚全国优质课程资源，助力高等教育数字化转型，为每一位学习者提供高质量的在线学习体验。
        </p>
      </div>
    </div>

    <div class="features-section">
      <h2 class="section-title">平台特色</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <h3 class="feature-title">精品课程</h3>
          <p class="feature-description">汇聚全国顶尖高校的优质课程资源</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">👨‍🏫</div>
          <h3 class="feature-title">名师授课</h3>
          <p class="feature-description">来自知名高校的优秀教师团队</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3 class="feature-title">数据驱动</h3>
          <p class="feature-description">基于大数据分析的智能推荐系统</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🌐</div>
          <h3 class="feature-title">随时随地</h3>
          <p class="feature-description">支持多终端访问，学习不受时间地点限制</p>
        </div>
      </div>
    </div>

    <div class="stats-section">
      <h2 class="section-title">数据统计概览</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #6366f1, #8b5cf6)">
            <span>📚</span>
          </div>
          <div class="stat-info">
            <span class="stat-num">{{ statistics.total || 0 }}</span>
            <span class="stat-name">课程总数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #22c55e, #16a34a)">
            <span>🏛️</span>
          </div>
          <div class="stat-info">
            <span class="stat-num">{{ statistics.schools || 0 }}</span>
            <span class="stat-name">学校数量</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f59e0b, #d97706)">
            <span>👨‍🏫</span>
          </div>
          <div class="stat-info">
            <span class="stat-num">{{ statistics.teachers || 0 }}</span>
            <span class="stat-name">教师数量</span>
          </div>
        </div>
      </div>
    </div>

    <div class="about-section">
      <h2 class="section-title">关于我们</h2>
      <div class="about-content">
        <p>
          国家高等教育智慧教育平台是教育部主导建设的国家级在线教育平台，致力于整合全国优质教育资源，
          推动高等教育数字化转型，提升教育质量和公平性。
        </p>
        <p>
          平台汇聚了来自清华大学、北京大学、复旦大学等国内顶尖高校的精品课程，涵盖理学、工学、文学、管理学等多个学科领域，
          为广大师生提供免费、便捷、高质量的在线学习服务。
        </p>
        <p>
          我们的使命是：让优质教育触手可及，让每个学习者都能享受到最好的教育资源。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const statistics = ref({
  total: 0,
  schools: 0,
  teachers: 0,
  total_students: 0
})

const fetchStatistics = async () => {
  try {
    const response = await axios.get('/api/statistics')
    statistics.value = response.data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

onMounted(() => {
  fetchStatistics()
})
</script>

<style scoped>
.home-page {
  padding-bottom: 40px;
}

.hero-section {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
  border-radius: 24px;
  padding: 60px 40px;
  margin-bottom: 32px;
  color: white;
}

.hero-content {
  text-align: center;
}

.hero-icon {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  font-size: 48px;
}

.hero-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 16px;
}

.hero-title a {
  color: white;
  text-decoration: none;
}

.hero-description {
  font-size: 16px;
  line-height: 1.8;
  opacity: 0.95;
  margin: 0 0 32px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
}

.stat-label {
  font-size: 14px;
  opacity: 0.85;
  margin-top: 4px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 24px;
}

.features-section {
  margin-bottom: 32px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.feature-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.feature-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px;
}

.feature-description {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

.stats-section {
  margin-bottom: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-name {
  font-size: 14px;
  color: #64748b;
}

.about-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.about-content {
  line-height: 1.8;
  color: #475569;
}

.about-content p {
  margin: 0 0 16px;
}

.about-content p:last-child {
  margin-bottom: 0;
}
</style>
