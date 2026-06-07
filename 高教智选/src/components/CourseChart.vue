<template>
  <div>
    <h2 class="text-xl font-bold text-gray-800 mb-6">数据可视化</h2>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>选课人次排行 Top 10</span>
          </template>
          <div ref="barChart" style="width: 100%; height: 320px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>课程来源分布</span>
          </template>
          <div ref="pieChart" style="width: 100%; height: 320px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-6">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>教师授课数量 Top 10</span>
          </template>
          <div ref="teacherChart" style="width: 100%; height: 320px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>数据统计概览</span>
          </template>
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon text-blue-500 mb-2">📚</div>
                <div class="stat-value">{{ stats.total }}</div>
                <div class="stat-label">课程总数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon text-green-500 mb-2">🏛️</div>
                <div class="stat-value">{{ stats.schools }}</div>
                <div class="stat-label">学校数量</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon text-purple-500 mb-2">👨‍🏫</div>
                <div class="stat-value">{{ stats.teachers }}</div>
                <div class="stat-label">教师数量</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon text-orange-500 mb-2">👥</div>
                <div class="stat-value">{{ Math.floor(stats.totalStudents / 10) }}</div>
                <div class="stat-label">总选课人次(十万)</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
const echarts = window.echarts
import axios from 'axios'

const barChart = ref(null)
const pieChart = ref(null)
const teacherChart = ref(null)

let barChartInstance = null
let pieChartInstance = null
let teacherChartInstance = null

const stats = ref({
  total: 0,
  schools: 0,
  teachers: 0,
  totalStudents: 0
})

const topCourses = ref([])
const schoolDistribution = ref([])

const mockTopCourses = [
  { name: '军事理论-综合版', value: 1400 },
  { name: '形势与政策', value: 1200 },
  { name: '大学生心理健康', value: 700 },
  { name: 'Python语言程序设计', value: 500 },
  { name: '心理学与生活', value: 450 },
  { name: '大学物理', value: 400 },
  { name: '高等数学', value: 380 },
  { name: '线性代数', value: 350 },
  { name: '计算机基础', value: 320 },
  { name: '大学英语', value: 300 }
]

const mockSchools = [
  { name: '北京大学', value: 35 },
  { name: '清华大学', value: 30 },
  { name: '浙江大学', value: 28 },
  { name: '复旦大学', value: 25 },
  { name: '上海交通大学', value: 22 },
  { name: '南京大学', value: 20 },
  { name: '中国人民大学', value: 18 },
  { name: '武汉大学', value: 15 },
  { name: '其他', value: 307 }
]

const mockTeachers = [
  { name: '孙华', value: 8 },
  { name: '王海军', value: 6 },
  { name: '杨振斌', value: 5 },
  { name: '嵩天', value: 5 },
  { name: '李红', value: 4 },
  { name: '张伟', value: 4 },
  { name: '李明', value: 3 },
  { name: '王芳', value: 3 },
  { name: '刘洋', value: 3 },
  { name: '陈静', value: 2 }
]

const fetchStatistics = async () => {
  try {
    const response = await axios.get('/api/statistics')
    stats.value = {
      total: response.data.total || 0,
      schools: response.data.schools || 0,
      teachers: response.data.teachers || 0,
      totalStudents: response.data.total_students || 0
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    stats.value = { total: 500, schools: 182, teachers: 451, totalStudents: 17260 }
  }
}

const fetchTopCourses = async () => {
  try {
    const response = await axios.get('/api/top_courses')
    topCourses.value = response.data.map(item => ({
      name: item.title || '未知课程',
      value: parseInt(item.students?.replace(/[^\d]/g, '')) || 0
    }))
  } catch (error) {
    console.error('获取热门课程失败:', error)
    topCourses.value = mockTopCourses
  }
}

const fetchSchoolDistribution = async () => {
  try {
    const response = await axios.get('/api/school_distribution')
    schoolDistribution.value = response.data.map(item => ({
      name: item.school || '未知学校',
      value: item.count || 0
    }))
  } catch (error) {
    console.error('获取学校分布失败:', error)
    schoolDistribution.value = mockSchools
  }
}

const initCharts = () => {
  setTimeout(() => {
    const coursesData = topCourses.value.length > 0 ? topCourses.value : mockTopCourses
    const schoolsData = schoolDistribution.value.length > 0 ? schoolDistribution.value : mockSchools

    if (barChart.value) {
      try {
        barChartInstance = echarts.init(barChart.value)
        barChartInstance.setOption({
          tooltip: { 
            trigger: 'axis', 
            axisPointer: { type: 'shadow' },
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#e2e8f0',
            borderWidth: 1,
            textStyle: { color: '#334155' },
            formatter: '{b}: {c}万'
          },
          grid: { left: '3%', right: '4%', bottom: '18%', top: '12%', containLabel: true },
          xAxis: { 
            type: 'category', 
            data: coursesData.map(item => item.name), 
            axisLabel: { rotate: 45, fontSize: 11, color: '#64748b' },
            axisLine: { lineStyle: { color: '#e2e8f0' } },
            axisTick: { show: false }
          },
          yAxis: { 
            type: 'value', 
            name: '选课人次(万)',
            nameTextStyle: { color: '#64748b', fontSize: 12 },
            axisLabel: { color: '#64748b' },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }
          },
          series: [{ 
            type: 'bar', 
            data: coursesData.map(item => item.value), 
            barWidth: '50%',
            itemStyle: { 
              borderRadius: [6, 6, 0, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#6366f1' },
                { offset: 1, color: '#8b5cf6' }
              ])
            },
            emphasis: {
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#4f46e5' },
                  { offset: 1, color: '#7c3aed' }
                ])
              }
            }
          }]
        })
      } catch (e) {
        console.error('Failed to init bar chart:', e)
      }
    }

    if (pieChart.value) {
      try {
        pieChartInstance = echarts.init(pieChart.value)
        const colors = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#14b8a6']
        pieChartInstance.setOption({
          tooltip: { 
            trigger: 'item',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#e2e8f0',
            borderWidth: 1,
            textStyle: { color: '#334155' },
            formatter: '{b}: {c}门 ({d}%)'
          },
          legend: { 
            orient: 'vertical', 
            left: '5%', 
            bottom: '10%', 
            fontSize: 11,
            textStyle: { color: '#64748b' },
            itemWidth: 12,
            itemHeight: 12,
            itemGap: 10
          },
          series: [{ 
            type: 'pie', 
            radius: ['45%', '75%'], 
            center: ['58%', '50%'], 
            data: schoolsData.map((item, index) => ({
              ...item,
              itemStyle: { color: colors[index % colors.length] }
            })),
            emphasis: { 
              itemStyle: { 
                shadowBlur: 20, 
                shadowOffsetX: 0, 
                shadowColor: 'rgba(0, 0, 0, 0.15)' 
              } 
            },
            label: {
              fontSize: 10,
              color: '#475569',
              formatter: '{b}\n{d}%'
            },
            labelLine: {
              length: 10,
              length2: 5,
              lineStyle: { color: '#cbd5e1' }
            }
          }]
        })
      } catch (e) {
        console.error('Failed to init pie chart:', e)
      }
    }

    if (teacherChart.value) {
      try {
        teacherChartInstance = echarts.init(teacherChart.value)
        teacherChartInstance.setOption({
          tooltip: { 
            trigger: 'axis', 
            axisPointer: { type: 'shadow' },
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#e2e8f0',
            borderWidth: 1,
            textStyle: { color: '#334155' },
            formatter: '{b}: {c}门'
          },
          grid: { left: '3%', right: '4%', bottom: '18%', top: '12%', containLabel: true },
          xAxis: { 
            type: 'category', 
            data: mockTeachers.map(item => item.name), 
            axisLabel: { rotate: 45, fontSize: 11, color: '#64748b' },
            axisLine: { lineStyle: { color: '#e2e8f0' } },
            axisTick: { show: false }
          },
          yAxis: { 
            type: 'value', 
            name: '课程数量',
            nameTextStyle: { color: '#64748b', fontSize: 12 },
            axisLabel: { color: '#64748b' },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }
          },
          series: [{ 
            type: 'bar', 
            data: mockTeachers.map(item => item.value), 
            barWidth: '50%',
            itemStyle: { 
              borderRadius: [6, 6, 0, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#ec4899' },
                { offset: 1, color: '#f43f5e' }
              ])
            },
            emphasis: {
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#db2777' },
                  { offset: 1, color: '#e11d48' }
                ])
              }
            }
          }]
        })
      } catch (e) {
        console.error('Failed to init teacher chart:', e)
      }
    }
  }, 300)
}

const handleResize = () => {
  barChartInstance?.resize()
  pieChartInstance?.resize()
  teacherChartInstance?.resize()
}

onMounted(async () => {
  await fetchStatistics()
  await fetchTopCourses()
  await fetchSchoolDistribution()
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  barChartInstance?.dispose()
  pieChartInstance?.dispose()
  teacherChartInstance?.dispose()
})
</script>
