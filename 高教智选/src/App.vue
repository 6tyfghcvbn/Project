<template>
  <router-view v-if="currentUser" />
  <LoginRegister v-else @login="handleLogin" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LoginRegister from './components/LoginRegister.vue'

const currentUser = ref(null)

const handleLogin = (user) => {
  currentUser.value = user
  localStorage.setItem('currentUser', JSON.stringify(user))
}

onMounted(() => {
  const savedUser = localStorage.getItem('currentUser')
  if (savedUser) {
    currentUser.value = JSON.parse(savedUser)
    setTimeout(() => {
      window.location.href = '#/'
    }, 100)
  }
})
</script>