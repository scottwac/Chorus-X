<template>
  <div class="flex gap-6 max-w-[1800px] mx-auto">
    <!-- Debug Sidebar (Left) -->
    <div 
      v-if="showDebugSidebar" 
      class="w-96 flex-shrink-0 bg-white rounded-xl shadow-md p-6 max-h-[calc(100vh-100px)] overflow-y-auto sticky top-6"
    >
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-800">🔍 Chorus Debug</h2>
        <button
          @click="showDebugSidebar = false"
          class="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>

      <div v-if="lastDebugInfo">
        <!-- Intent -->
        <div class="mb-4 p-3 bg-blue-50 rounded-lg">
          <div class="text-xs font-semibold text-blue-700 mb-1">Intent</div>
          <div class="text-sm text-blue-900">{{ lastDebugInfo.intent_detected || 'N/A' }}</div>
        </div>

        <!-- RAG Count -->
        <div v-if="lastDebugInfo.rag_count_used" class="mb-4 p-3 bg-green-50 rounded-lg">
          <div class="text-xs font-semibold text-green-700 mb-1">RAG Chunks Used</div>
          <div class="text-sm text-green-900">{{ lastDebugInfo.rag_count_used }}</div>
        </div>

        <!-- All Responses -->
        <div v-if="lastDebugInfo.all_responses && lastDebugInfo.all_responses.length > 0" class="mb-4">
          <div class="text-sm font-semibold text-gray-700 mb-2">
            📝 All Responses ({{ lastDebugInfo.all_responses.length }})
          </div>
          <div class="space-y-3">
            <div
              v-for="(resp, idx) in lastDebugInfo.all_responses"
              :key="idx"
              class="p-3 rounded-lg border"
              :class="idx === lastDebugInfo.winner_index ? 'bg-yellow-50 border-yellow-300' : 'bg-gray-50 border-gray-200'"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="text-xs font-semibold text-gray-700">
                  Response {{ idx + 1 }}
                  <span v-if="idx === lastDebugInfo.winner_index" class="ml-2 text-yellow-600">👑 Winner</span>
                </div>
                <div class="text-xs text-gray-500">
                  {{ resp.provider }} / {{ resp.model }}
                </div>
              </div>
              <div class="text-xs text-gray-600 line-clamp-4">{{ resp.response }}</div>
            </div>
          </div>
        </div>

        <!-- Votes -->
        <div v-if="lastDebugInfo.votes && lastDebugInfo.votes.length > 0" class="mb-4">
          <div class="text-sm font-semibold text-gray-700 mb-2">🗳️ Votes</div>
          <div class="space-y-2">
            <div
              v-for="(vote, idx) in lastDebugInfo.votes"
              :key="idx"
              class="p-2 bg-purple-50 rounded text-xs"
            >
              <div class="font-semibold text-purple-700">{{ vote.evaluator }}</div>
              <div class="text-purple-900">Voted for Response {{ vote.vote + 1 }}</div>
            </div>
          </div>
        </div>

        <!-- Vote Counts -->
        <div v-if="lastDebugInfo.vote_counts" class="mb-4">
          <div class="text-sm font-semibold text-gray-700 mb-2">📊 Vote Summary</div>
          <div class="space-y-1">
            <div
              v-for="(count, responseIdx) in lastDebugInfo.vote_counts"
              :key="responseIdx"
              class="flex items-center justify-between p-2 bg-gray-50 rounded text-xs"
            >
              <span class="font-medium">Response {{ parseInt(responseIdx) + 1 }}</span>
              <div class="flex items-center gap-2">
                <div class="w-24 bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-chorus-green-500 h-2 rounded-full"
                    :style="{ width: `${(count / Math.max(...Object.values(lastDebugInfo.vote_counts))) * 100}%` }"
                  ></div>
                </div>
                <span class="font-semibold">{{ count }} vote{{ count !== 1 ? 's' : '' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Image Search Debug -->
        <div v-if="lastDebugInfo.images_found !== undefined" class="mb-4 p-3 bg-indigo-50 rounded-lg">
          <div class="text-xs font-semibold text-indigo-700 mb-1">Images Found</div>
          <div class="text-sm text-indigo-900">{{ lastDebugInfo.images_found }} / {{ lastDebugInfo.total_docs_searched }} searched</div>
        </div>
      </div>

      <div v-else class="text-sm text-gray-500 text-center py-8">
        Send a message to see debug info
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="flex-1 min-w-0">
      <!-- Header -->
      <div class="bg-white rounded-xl shadow-md p-6 mb-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <button
              @click="$router.push('/bots')"
              class="text-2xl hover:bg-gray-100 p-2 rounded-lg"
            >
              ← 
            </button>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-2xl">🤖</span>
                <h1 class="text-2xl font-bold text-gray-800">{{ bot?.name || 'Loading...' }}</h1>
              </div>
              <p class="text-sm text-gray-600 mt-1">{{ bot?.instructions }}</p>
            </div>
          </div>
        
      <div class="flex gap-2 items-center flex-wrap">
        <!-- RAG Settings -->
        <div class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg bg-white">
          <label class="text-sm font-medium text-gray-700">RAG:</label>
          <input
            v-model.number="ragCount"
            type="number"
            min="1"
            max="20"
            class="w-16 px-2 py-1 border border-gray-300 rounded text-sm"
          />
          <span class="text-xs text-gray-500">chunks</span>
        </div>

        <!-- Image Search Settings Toggle -->
        <button
          @click="showImageSettings = !showImageSettings"
          class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 text-sm font-medium text-gray-700"
        >
          🖼️ Image Search
          <span class="text-xs text-gray-500">{{ showImageSettings ? '▲' : '▼' }}</span>
        </button>
          <button
            @click="showDebugSidebar = !showDebugSidebar"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium"
            :class="showDebugSidebar ? 'bg-blue-50 text-blue-700 border-blue-300' : ''"
          >
            {{ showDebugSidebar ? '🔍 Hide Debug Panel' : '🔍 Show Debug Panel' }}
          </button>
          <button
            @click="clearHistory"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
          >
            🗑️ Clear History
          </button>
        </div>
      </div>
    </div>

      <!-- Image Search Settings Panel -->
      <div v-if="showImageSettings" class="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-3">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-3">
            <label class="text-sm font-medium text-gray-700">Max Images:</label>
            <input
              v-model.number="imageSearchSettings.maxResults"
              type="number"
              min="1"
              max="10"
              class="w-16 px-2 py-1 border border-gray-300 rounded text-sm"
            />
          </div>

          <div class="flex items-center gap-3">
            <label class="text-sm font-medium text-gray-700">Min Confidence:</label>
            <input
              v-model.number="imageSearchSettings.minConfidence"
              type="number"
              min="0"
              max="1"
              step="0.05"
              class="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
            />
            <span class="text-xs text-gray-600">{{ Math.round(imageSearchSettings.minConfidence * 100) }}%</span>
          </div>

          <div class="text-xs text-gray-600 ml-auto">
            💡 Filters out low-confidence image matches
          </div>
        </div>
      </div>

      <!-- Chat Container -->
      <div class="bg-white rounded-xl shadow-md flex flex-col h-[calc(100vh-300px)]">
      <!-- Messages -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
        <div v-if="messages.length === 0" class="text-center text-gray-500 mt-12">
          <div class="text-6xl mb-4">💬</div>
          <p>Start a conversation with {{ bot?.name }}</p>
        </div>

        <div
          v-for="(message, idx) in messages"
          :key="idx"
          class="flex gap-3"
          :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            v-if="message.role === 'assistant'"
            class="flex-shrink-0 w-8 h-8 bg-chorus-green-100 rounded-full flex items-center justify-center"
          >
            🤖
          </div>
          
          <div
            class="max-w-[70%] rounded-2xl px-4 py-3"
            :class="message.role === 'user' 
              ? 'bg-chorus-green-600 text-white' 
              : 'bg-gray-100 text-gray-800'"
          >
            <div class="whitespace-pre-wrap">{{ message.content }}</div>
            
            <!-- Images Display (Found Images) -->
            <div v-if="message.images && message.images.length > 0" class="mt-4 space-y-3">
              <div
                v-for="(image, imgIdx) in message.images"
                :key="imgIdx"
                class="border border-gray-300 rounded-lg p-3 bg-white"
              >
                <div class="font-semibold text-sm mb-2">{{ image.filename }}</div>
                <img
                  :src="getImageUrl(image)"
                  :alt="image.filename"
                  class="max-w-full h-auto rounded cursor-pointer hover:opacity-90"
                  @click="openImageModal(image)"
                />
                <div class="text-xs text-gray-500 mt-2">
                  Relevance: {{ Math.round(image.relevance_score * 100) }}%
                </div>
              </div>
            </div>
            
            <!-- Generated Image Display -->
            <div v-if="message.generated_image" class="mt-4">
              <div class="border border-purple-300 rounded-lg p-3 bg-purple-50">
                <div class="font-semibold text-sm mb-2 text-purple-700">
                  {{ message.generated_image.is_edit ? '✨ Edited Image' : '🎨 Generated Image' }}
                </div>
                <img
                  :src="getGeneratedImageUrl(message.generated_image.filename)"
                  :alt="message.generated_image.prompt"
                  class="max-w-full h-auto rounded cursor-pointer hover:opacity-90 border-2 border-purple-200"
                  @click="openGeneratedImageModal(message.generated_image)"
                />
                <div class="text-xs text-purple-600 mt-2 italic">
                  "{{ message.generated_image.prompt }}"
                </div>
              </div>
            </div>
            
            <!-- Generated Chart Display -->
            <div v-if="message.generated_chart" class="mt-4">
              <div class="border border-blue-300 rounded-lg p-3 bg-blue-50">
                <div class="font-semibold text-sm mb-2 text-blue-700">
                  📊 {{ message.generated_chart.title }}
                </div>
                <img
                  :src="getGeneratedChartUrl(message.generated_chart.filename)"
                  :alt="message.generated_chart.title"
                  class="max-w-full h-auto rounded cursor-pointer hover:opacity-90 border-2 border-blue-200 bg-white"
                  @click="openGeneratedChartModal(message.generated_chart)"
                />
                <div class="text-xs text-blue-600 mt-2">
                  Chart Type: {{ message.generated_chart.chart_type }}
                </div>
              </div>
            </div>
            
            <!-- Intent Badge -->
            <div v-if="message.intent && message.intent !== 'text'" class="mt-2">
              <span class="inline-block px-2 py-1 text-xs rounded-full" 
                    :class="getIntentBadgeClass(message.intent)">
                {{ getIntentBadgeText(message.intent) }}
              </span>
            </div>
            
            <!-- Debug Info -->
            <div v-if="showDebug && message.debug" class="mt-3 pt-3 border-t border-gray-300">
              <div class="text-xs font-semibold mb-2">Debug Information:</div>
              
              <!-- Intent Info -->
              <div v-if="message.debug.intent_detected" class="text-xs mb-2">
                <span class="font-semibold">Intent:</span> {{ message.debug.intent_detected }}
                <span v-if="message.debug.rag_count_used" class="ml-2">
                  | <span class="font-semibold">RAG Chunks:</span> {{ message.debug.rag_count_used }}
                </span>
              </div>
              
              <!-- All Responses -->
              <div class="text-xs mb-2">
                <div class="font-semibold mb-1">All Responses ({{ message.debug.all_responses?.length }}):</div>
                <div v-for="(resp, i) in message.debug.all_responses" :key="i" class="mb-2 p-2 bg-white rounded">
                  <div class="font-semibold">{{ resp.provider }} / {{ resp.model }}</div>
                  <div class="text-gray-600 mt-1">{{ resp.response.substring(0, 100) }}...</div>
                </div>
              </div>
              
              <!-- Votes -->
              <div v-if="message.debug.votes" class="text-xs">
                <div class="font-semibold mb-1">Votes:</div>
                <div v-for="(vote, i) in message.debug.votes" :key="i" class="text-gray-600">
                  {{ vote.evaluator }} voted for Response {{ vote.vote + 1 }}
                </div>
                <div class="mt-1 font-semibold">
                  Winner: Response {{ message.debug.winner_index + 1 }}
                </div>
              </div>
            </div>
          </div>
          
          <div
            v-if="message.role === 'user'"
            class="flex-shrink-0 w-8 h-8 bg-chorus-green-600 rounded-full flex items-center justify-center text-white"
          >
            👤
          </div>
        </div>

        <!-- Loading Indicator -->
        <div v-if="loading" class="flex gap-3">
          <div class="flex-shrink-0 w-8 h-8 bg-chorus-green-100 rounded-full flex items-center justify-center">
            🤖
          </div>
          <div class="bg-gray-100 rounded-2xl px-4 py-3 min-w-[300px]">
            <div class="flex gap-2 items-center mb-2">
              <div class="animate-spin h-4 w-4 border-2 border-chorus-green-600 border-t-transparent rounded-full"></div>
              <span class="text-sm text-gray-700 font-medium">
                {{ processingStatus || 'Processing your request...' }}
              </span>
            </div>
            <!-- Show completed steps -->
            <div v-if="processingSteps.length > 0" class="mt-3 space-y-1 max-h-32 overflow-y-auto">
              <div 
                v-for="(step, idx) in processingSteps" 
                :key="idx"
                class="text-xs text-gray-600 flex items-start gap-2"
              >
                <span class="text-green-500 flex-shrink-0 mt-0.5">✓</span>
                <span>{{ step }}</span>
              </div>
            </div>
            <div v-else class="text-xs text-gray-500 italic">
              This may take 10-30 seconds depending on the query complexity
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="border-t border-gray-200 p-4">
        <div class="flex gap-3">
          <input
            v-model="inputMessage"
            @keypress.enter="sendMessage"
            type="text"
            placeholder="Type your message..."
            class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-chorus-green-500 focus:border-transparent"
            :disabled="loading"
          />
          <button
            @click="sendMessage"
            :disabled="loading || !inputMessage.trim()"
            class="px-6 py-3 bg-chorus-green-600 text-white rounded-xl hover:bg-chorus-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
          >
            Send 📤
          </button>
        </div>
        </div>
      </div>
    </div>

    <!-- Image Modal -->
    <div
      v-if="selectedImage"
      class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4"
      @click="selectedImage = null"
    >
      <div class="max-w-6xl max-h-[90vh] relative">
        <button
          @click="selectedImage = null"
          class="absolute -top-10 right-0 text-white text-3xl hover:text-gray-300"
        >
          ×
        </button>
        <img
          :src="selectedImage.isChart ? getGeneratedChartUrl(selectedImage.filename) : (selectedImage.isGenerated ? getGeneratedImageUrl(selectedImage.filename) : getImageUrl(selectedImage))"
          :alt="selectedImage.filename"
          class="max-w-full max-h-[90vh] object-contain"
        />
        <div class="text-white text-center mt-4">
          {{ selectedImage.isChart ? selectedImage.title : (selectedImage.isGenerated ? selectedImage.prompt : selectedImage.filename) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getBots, chatWithBot, getChatHistory, getFileImage } from '../api'

const route = useRoute()
const botId = parseInt(route.params.botId)

const bot = ref(null)
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const showDebug = ref(false)
const showDebugSidebar = ref(false)
const lastDebugInfo = ref(null)
const messagesContainer = ref(null)
const ragCount = ref(20)
const selectedImage = ref(null)
const processingStatus = ref('')
const processingSteps = ref([])

// Image search settings
const showImageSettings = ref(false)
const imageSearchSettings = ref({
  maxResults: 3,
  minConfidence: 0.6  // 60% minimum confidence
})

const loadBot = async () => {
  try {
    const response = await getBots()
    bot.value = response.data.find(b => b.id === botId)
    // Set initial RAG count from bot settings
    if (bot.value && bot.value.rag_results_count) {
      ragCount.value = bot.value.rag_results_count
    }
  } catch (error) {
    console.error('Failed to load bot:', error)
  }
}

const loadHistory = async () => {
  try {
    const response = await getChatHistory(botId)
    messages.value = response.data.map(h => ([
      { role: 'user', content: h.user_message },
      { role: 'assistant', content: h.bot_response }
    ])).flat()
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Failed to load chat history:', error)
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value
  inputMessage.value = ''

  // Add user message
  messages.value.push({
    role: 'user',
    content: userMessage
  })

  await nextTick()
  scrollToBottom()

  loading.value = true
  processingSteps.value = []
  processingStatus.value = 'Connecting...'

  try {
    // Use EventSource for real-time SSE updates
    const params = new URLSearchParams({
      message: userMessage,
      rag_count: ragCount.value.toString()
    })
    
    const streamUrl = `http://localhost:5000/api/bots/${botId}/chat/stream?${params.toString()}`
    const eventSource = new EventSource(streamUrl)
    
    // Handle status updates
    eventSource.addEventListener('status', (event) => {
      const data = JSON.parse(event.data)
      processingSteps.value.push(data.message)
      processingStatus.value = data.message
      scrollToBottom()
    })
    
    // Handle final response
    eventSource.addEventListener('final', (event) => {
      const data = JSON.parse(event.data)
      
      // Close the connection
      eventSource.close()
      loading.value = false
      processingSteps.value = []
      processingStatus.value = ''
      
      // Add bot response
      messages.value.push({
        role: 'assistant',
        content: data.response,
        intent: data.intent,
        images: data.images || [],
        generated_image: data.generated_image || null,
        generated_chart: data.generated_chart || null,
        debug: data.debug
      })
      
      // Update debug sidebar
      if (data.debug) {
        lastDebugInfo.value = data.debug
      }
      
      scrollToBottom()
    })
    
    // Handle errors
    eventSource.addEventListener('error', (event) => {
      const data = event.data ? JSON.parse(event.data) : null
      
      eventSource.close()
      loading.value = false
      processingSteps.value = []
      processingStatus.value = ''
      
      messages.value.push({
        role: 'assistant',
        content: data?.message || 'Sorry, I encountered an error. Please try again.'
      })
      
      scrollToBottom()
    })
    
    // Handle connection errors
    eventSource.onerror = (error) => {
      console.error('EventSource error:', error)
      eventSource.close()
      loading.value = false
      processingSteps.value = []
      processingStatus.value = ''
      
      messages.value.push({
        role: 'assistant',
        content: 'Sorry, the connection was interrupted. Please try again.'
      })
      
      scrollToBottom()
    }
    
  } catch (error) {
    console.error('Failed to send message:', error)
    loading.value = false
    processingSteps.value = []
    processingStatus.value = ''
    
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.'
    })
  }
}

const getImageUrl = (image) => {
  // Get bot's dataset ID
  if (!bot.value || !bot.value.dataset_id) return ''
  return getFileImage(bot.value.dataset_id, image.file_id)
}

const getGeneratedImageUrl = (filename) => {
  return `http://localhost:5000/api/generated-images/${filename}`
}

const getGeneratedChartUrl = (filename) => {
  return `http://localhost:5000/api/generated-charts/${filename}`
}

const openImageModal = (image) => {
  selectedImage.value = image
}

const openGeneratedImageModal = (generatedImage) => {
  // Create a fake image object for the modal
  selectedImage.value = {
    filename: generatedImage.filename,
    isGenerated: true,
    prompt: generatedImage.prompt
  }
}

const openGeneratedChartModal = (generatedChart) => {
  // Create a fake image object for the modal
  selectedImage.value = {
    filename: generatedChart.filename,
    isChart: true,
    title: generatedChart.title
  }
}

const getIntentBadgeClass = (intent) => {
  const classes = {
    'find_image': 'bg-blue-100 text-blue-700',
    'generate_image': 'bg-purple-100 text-purple-700',
    'generate_chart': 'bg-green-100 text-green-700'
  }
  return classes[intent] || 'bg-gray-100 text-gray-700'
}

const getIntentBadgeText = (intent) => {
  const texts = {
    'find_image': '🖼️ Image Search',
    'generate_image': '🎨 Image Generation',
    'generate_chart': '📊 Chart Generation'
  }
  return texts[intent] || intent
}

const clearHistory = async () => {
  if (confirm('Are you sure you want to clear the chat history?')) {
    try {
      // Clear backend history
      await fetch(`http://localhost:5000/api/bots/${botId}/history`, {
        method: 'DELETE'
      })
      // Clear frontend state
      messages.value = []
    } catch (error) {
      console.error('Failed to clear history:', error)
      // Still clear frontend state even if backend fails
      messages.value = []
    }
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

onMounted(() => {
  loadBot()
  loadHistory()
})
</script>

<style scoped>
.animation-delay-200 {
  animation-delay: 0.2s;
}

.animation-delay-400 {
  animation-delay: 0.4s;
}

.line-clamp-4 {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

