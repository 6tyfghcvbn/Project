<template>
  <div>
    <div class="header-section">
      <h2 class="page-title">课程列表</h2>
    </div>
    <div class="search-section">
      <el-input 
        v-model="searchKeyword" 
        placeholder="搜索课程名称或学校" 
        class="search-input"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch" class="search-btn" />
        </template>
      </el-input>
    </div>
    
    <el-table :data="courses" border style="width: 100%" :loading="loading" class="course-table">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="课程名称" min-width="200">
        <template #default="scope">
          <a :href="scope.row.link" target="_blank" class="course-title-link">
            {{ scope.row.title }}
          </a>
        </template>
      </el-table-column>
      <el-table-column prop="school" label="学校" width="150" />
      <el-table-column prop="teacher" label="授课教师" width="120" />
      <el-table-column prop="students" label="选课人次" width="120" />
      <el-table-column prop="created_at" label="添加时间" width="180" />
    </el-table>
    
    <el-pagination 
      v-if="total > 0"
      :current-page="currentPage" 
      :page-size="pageSize" 
      :total="total"
      @current-change="handlePageChange"
      layout="total, prev, pager, next, jumper"
      class="mt-6 flex justify-center"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const courses = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const fetchCourses = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/courses', {
      params: {
        page: currentPage.value,
        size: pageSize.value,
        keyword: searchKeyword.value
      }
    })
    courses.value = response.data.data
    total.value = response.data.total
  } catch (error) {
    console.error('获取课程列表失败:', error)
    courses.value = mockCourses
    total.value = mockCourses.length
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchCourses()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchCourses()
}

const mockCourses = [
  { id: 1, title: '军事理论-综合版', school: '北京大学', teacher: '孙华', students: '1400万+', link: 'https://higher.smartedu.cn/course/69deb65c95df98bb27ab2e93', created_at: '2024-01-15 10:30:00' },
  { id: 2, title: '高等数学', school: '清华大学', teacher: '李明', students: '800万+', link: 'https://higher.smartedu.cn/course/test2', created_at: '2024-01-14 09:20:00' },
  { id: 3, title: '大学物理', school: '复旦大学', teacher: '王芳', students: '600万+', link: 'https://higher.smartedu.cn/course/test3', created_at: '2024-01-13 14:45:00' },
  { id: 4, title: '计算机基础', school: '浙江大学', teacher: '张伟', students: '1200万+', link: 'https://higher.smartedu.cn/course/test4', created_at: '2024-01-12 11:00:00' },
  { id: 5, title: '英语听说', school: '上海交通大学', teacher: '刘洋', students: '900万+', link: 'https://higher.smartedu.cn/course/test5', created_at: '2024-01-11 16:30:00' }
]

onMounted(() => {
  fetchCourses()
})
</script>