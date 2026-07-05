import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../components/MainLayout.vue'
import HomePage from '../components/HomePage.vue'
import CourseList from '../components/CourseList.vue'
import CourseDetail from '../components/CourseDetail.vue'
import CourseChart from '../components/CourseChart.vue'
import ChatAssistant from '../components/ChatAssistant.vue'
import UserSettings from '../components/UserSettings.vue'
import AvatarSettings from '../components/AvatarSettings.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', name: 'home', component: HomePage },
      { path: 'home', name: 'home', component: HomePage },
      { path: 'courses', name: 'courses', component: CourseList },
      { path: 'courses/:id', name: 'course-detail', component: CourseDetail },
      { path: 'chart', name: 'chart', component: CourseChart },
      { path: 'assistant', name: 'assistant', component: ChatAssistant },
      { path: 'settings', name: 'settings', component: UserSettings },
      { path: 'avatar-settings', name: 'avatar-settings', component: AvatarSettings }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router