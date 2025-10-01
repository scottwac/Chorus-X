<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-chorus-green-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg border-b-4 border-chorus-green-500">
      <div class="container mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="text-3xl font-bold bg-gradient-to-r from-chorus-green-600 to-chorus-green-400 bg-clip-text text-transparent">
              Chorus
            </div>
            <div class="text-sm text-gray-500">Multi-LLM Orchestration</div>
            
            <!-- Connection Status -->
            <div class="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium"
                 :class="isConnected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
              <div class="relative">
                <div class="w-2 h-2 rounded-full"
                     :class="isConnected ? 'bg-green-500' : 'bg-red-500'"></div>
                <div v-if="isConnected" class="absolute inset-0 w-2 h-2 rounded-full bg-green-500 animate-ping"></div>
              </div>
              <span>{{ isConnected ? 'Connected' : 'Disconnected' }}</span>
            </div>
          </div>
          
          <div class="flex space-x-1">
            <router-link
              to="/datasets"
              class="px-4 py-2 rounded-lg font-medium hover:bg-chorus-green-50"
              :class="$route.path === '/datasets' ? 'bg-chorus-green-100 text-chorus-green-700' : 'text-gray-600'"
            >
              📁 Datasets
            </router-link>
            <router-link
              to="/chorus-models"
              class="px-4 py-2 rounded-lg font-medium hover:bg-chorus-green-50"
              :class="$route.path === '/chorus-models' ? 'bg-chorus-green-100 text-chorus-green-700' : 'text-gray-600'"
            >
              🎭 Chorus Models
            </router-link>
            <router-link
              to="/bots"
              class="px-4 py-2 rounded-lg font-medium hover:bg-chorus-green-50"
              :class="$route.path === '/bots' || $route.path.startsWith('/chat') ? 'bg-chorus-green-100 text-chorus-green-700' : 'text-gray-600'"
            >
              🤖 Bots
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Disconnection Warning Banner -->
    <div v-if="!isConnected" class="bg-red-500 text-white px-6 py-3">
      <div class="container mx-auto flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-xl">⚠️</span>
          <div>
            <div class="font-semibold">Cannot connect to Flask Server</div>
            <div class="text-sm opacity-90">Make sure the server is running on http://localhost:5000</div>
          </div>
        </div>
        <button
          @click="checkHealth"
          class="px-4 py-2 bg-white text-red-600 rounded-lg hover:bg-red-50 font-medium text-sm"
        >
          Retry Connection
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto px-6 py-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useHealthCheck } from './composables/useHealthCheck'

const { isConnected, checkHealth } = useHealthCheck(10000) // Check every 10 seconds
</script>

