<template>
  <div class="max-w-6xl mx-auto">
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
            @click="showDebug = !showDebug"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
          >
            {{ showDebug ? '🔍 Hide Debug' : '🔍 Show Debug' }}
          </button>
          <button
            @click="clearHistory"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
          >
            🗑️ Clear History
          </button>
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
            
            <!-- Intent Badge -->
            <div v-if="message.intent && message.intent !== 'text'" class="mt-2">
              <span class="inline-block px-2 py-1 text-xs rounded-full" 
                    :class="message.intent === 'find_image' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'">
                {{ message.intent === 'find_image' ? '🖼️ Image Search' : '🎨 Image Generation' }}
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
                  {{ vote.evaluator }} voted for Response {{ vote.vote }}
                </div>
                <div class="mt-1 font-semibold">
                  Winner: Response {{ message.debug.winner_index }}
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
          <div class="bg-gray-100 rounded-2xl px-4 py-3">
            <div class="flex gap-2 items-center">
              <div class="animate-bounce">●</div>
              <div class="animate-bounce animation-delay-200">●</div>
              <div class="animate-bounce animation-delay-400">●</div>
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
          :src="selectedImage.isGenerated ? getGeneratedImageUrl(selectedImage.filename) : getImageUrl(selectedImage)"
          :alt="selectedImage.filename"
          class="max-w-full max-h-[90vh] object-contain"
        />
        <div class="text-white text-center mt-4">
          {{ selectedImage.isGenerated ? selectedImage.prompt : selectedImage.filename }}
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
const messagesContainer = ref(null)
const ragCount = ref(5)
const selectedImage = ref(null)

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

  try {
    // Send message with current RAG count and image search settings
    const response = await chatWithBot(
      botId, 
      userMessage, 
      ragCount.value,
      imageSearchSettings.value
    )
    
    // Add bot response (filtering already done on backend)
    messages.value.push({
      role: 'assistant',
      content: response.data.response,
      intent: response.data.intent,
      images: response.data.images || [],
      generated_image: response.data.generated_image || null,
      debug: response.data.debug
    })

    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Failed to send message:', error)
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.'
    })
  } finally {
    loading.value = false
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

const clearHistory = () => {
  if (confirm('Are you sure you want to clear the chat history?')) {
    messages.value = []
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
</style>

