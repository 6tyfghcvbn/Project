<template>
  <div class="course-detail">
    <el-card v-if="course" shadow="hover">
      <div class="flex gap-6">
        <div class="w-48 h-32 bg-gray-100 rounded-lg flex items-center justify-center">
          <img 
            :src="course.image || 'https://via.placeholder.com/200x150'" 
            :alt="course.title" 
            class="max-w-full max-h-full object-contain rounded-lg"
          />
        </div>
        <div class="flex-1">
          <h2 class="text-2xl font-bold text-gray-800 mb-2">{{ course.title }}</h2>
          <div class="flex gap-4 text-sm text-gray-600">
            <span class="flex items-center">
              <el-icon class="mr-1" name="School" />
              {{ course.school }}
            </span>
            <span class="flex items-center">
              <el-icon class="mr-1" name="User" />
              {{ course.teacher }}
            </span>
            <span class="flex items-center">
              <el-icon class="mr-1" name="Users" />
              {{ course.students }}人次
            </span>
          </div>
        </div>
      </div>
      
      <div class="mt-6 pt-6 border-t">
        <h3 class="text-lg font-semibold mb-3">课程信息</h3>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="课程来源" :value="course.school" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="授课教师" :value="course.teacher" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="选课人次" :value="course.students" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="课程链接" :value="'点击查看'" />
          </el-col>
        </el-row>
      </div>
      
      <div class="mt-4">
        <el-button type="primary" @click="openCourse">
          <el-icon name="Link" />
          访问课程
        </el-button>
        <el-button @click="goBack">
          <el-icon name="ArrowLeft" />
          返回列表
        </el-button>
      </div>
    </el-card>
    
    <el-card v-else shadow="hover">
      <div class="text-center py-12">
        <el-icon name="Search" class="text-4xl text-gray-300 mb-4" />
        <p class="text-gray-500">未找到课程信息</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const course = ref(null)

const fetchCourse = async () => {
  const id = route.params.id
  try {
    const response = await axios.get(`/api/courses/${id}`)
    course.value = response.data
  } catch (error) {
    console.error('获取课程详情失败:', error)
    course.value = {
      id: id,
      title: '军事理论-综合版',
      school: '北京大学',
      teacher: '孙华',
      students: '1400万+',
      link: 'https://higher.smartedu.cn/course/69deb65c95df98bb27ab2e93'
    }
  }
}

const openCourse = () => {
  if (course.value?.link) {
    window.open(course.value.link, '_blank')
  }
}

const goBack = () => {
  router.push('/courses')
}

onMounted(() => {
  fetchCourse()
})
</script>