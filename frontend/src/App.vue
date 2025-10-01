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

    <!-- Main Content -->
    <main class="container mx-auto px-6 py-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
// No additional logic needed
</script>

