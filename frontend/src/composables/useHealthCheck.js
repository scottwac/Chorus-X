import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

export function useHealthCheck(interval = 10000) {
  const isConnected = ref(false)
  const lastChecked = ref(null)
  const checkInterval = ref(null)

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`, {
        timeout: 3000
      })
      
      if (response.status === 200 && response.data.status === 'healthy') {
        isConnected.value = true
        lastChecked.value = new Date()
      } else {
        isConnected.value = false
      }
    } catch (error) {
      isConnected.value = false
      console.warn('Health check failed:', error.message)
    }
  }

  const startHealthCheck = () => {
    // Check immediately
    checkHealth()
    
    // Then check periodically
    checkInterval.value = setInterval(checkHealth, interval)
  }

  const stopHealthCheck = () => {
    if (checkInterval.value) {
      clearInterval(checkInterval.value)
      checkInterval.value = null
    }
  }

  onMounted(() => {
    startHealthCheck()
  })

  onUnmounted(() => {
    stopHealthCheck()
  })

  return {
    isConnected,
    lastChecked,
    checkHealth,
    startHealthCheck,
    stopHealthCheck
  }
}

