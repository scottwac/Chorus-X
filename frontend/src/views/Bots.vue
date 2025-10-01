<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-800">Bots</h1>
        <p class="text-gray-600 mt-1">Create AI bots with custom instructions and knowledge</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="px-6 py-3 bg-chorus-green-600 text-white rounded-lg hover:bg-chorus-green-700 shadow-lg font-medium"
      >
        + New Bot
      </button>
    </div>

    <!-- Bots Grid -->
    <div v-if="bots.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="bot in bots"
        :key="bot.id"
        class="bg-white rounded-xl shadow-md hover:shadow-xl p-6 border-2 border-transparent hover:border-chorus-green-300 cursor-pointer"
        @click="navigateToChat(bot.id)"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-2xl">🤖</span>
              <h3 class="text-xl font-bold text-gray-800">{{ bot.name }}</h3>
            </div>
            <p class="text-sm text-gray-600 line-clamp-3">{{ bot.instructions }}</p>
          </div>
          <button
            @click.stop="deleteBotHandler(bot.id)"
            class="text-red-500 hover:text-red-700 text-xl"
          >
            🗑️
          </button>
        </div>

        <div class="space-y-2 text-sm">
          <div class="flex items-center gap-2 text-gray-600">
            <span>📁</span>
            <span>{{ getDatasetName(bot.dataset_id) }}</span>
          </div>
          <div class="flex items-center gap-2 text-gray-600">
            <span>🎭</span>
            <span>{{ getChorusModelName(bot.chorus_model_id) }}</span>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-gray-200">
          <button
            @click.stop="navigateToChat(bot.id)"
            class="w-full px-4 py-2 bg-chorus-green-100 text-chorus-green-700 rounded-lg hover:bg-chorus-green-200 font-medium"
          >
            💬 Start Chat
          </button>
        </div>

        <div class="text-xs text-gray-500 mt-3">
          Created {{ new Date(bot.created_at).toLocaleDateString() }}
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-16 bg-white rounded-xl shadow-md">
      <div class="text-6xl mb-4">🤖</div>
      <h3 class="text-xl font-semibold text-gray-800 mb-2">No bots yet</h3>
      <p class="text-gray-600 mb-6">Create your first bot to start chatting</p>
      <button
        @click="showCreateModal = true"
        class="px-6 py-3 bg-chorus-green-600 text-white rounded-lg hover:bg-chorus-green-700 font-medium"
      >
        Create Bot
      </button>
    </div>

    <!-- Create Bot Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-2xl">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Create New Bot</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Bot Name</label>
            <input
              v-model="newBot.name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chorus-green-500 focus:border-transparent"
              placeholder="Customer Support Bot"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Instructions</label>
            <textarea
              v-model="newBot.instructions"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chorus-green-500 focus:border-transparent"
              rows="4"
              placeholder="You are a helpful customer support assistant. Be friendly and professional..."
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Dataset</label>
            <select
              v-model="newBot.dataset_id"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chorus-green-500 focus:border-transparent"
            >
              <option :value="null">No dataset (general knowledge only)</option>
              <option v-for="dataset in datasets" :key="dataset.id" :value="dataset.id">
                {{ dataset.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Chorus Model</label>
            <select
              v-model="newBot.chorus_model_id"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chorus-green-500 focus:border-transparent"
            >
              <option :value="null">Select a Chorus model...</option>
              <option v-for="model in chorusModels" :key="model.id" :value="model.id">
                {{ model.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">RAG Results Count</label>
            <input
              v-model.number="newBot.rag_results_count"
              type="number"
              min="1"
              max="20"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chorus-green-500 focus:border-transparent"
              placeholder="5"
            />
            <p class="text-xs text-gray-500 mt-1">Number of relevant document chunks to retrieve (1-20)</p>
          </div>
        </div>

        <div class="flex space-x-4 mt-6">
          <button
            @click="showCreateModal = false"
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="createBotHandler"
            class="flex-1 px-4 py-2 bg-chorus-green-600 text-white rounded-lg hover:bg-chorus-green-700"
          >
            Create
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getBots, createBot, deleteBot, getDatasets, getChorusModels } from '../api'

const router = useRouter()
const bots = ref([])
const datasets = ref([])
const chorusModels = ref([])
const showCreateModal = ref(false)
const newBot = ref({
  name: '',
  instructions: '',
  dataset_id: null,
  chorus_model_id: null,
  rag_results_count: 5
})

const loadBots = async () => {
  try {
    const response = await getBots()
    bots.value = response.data
  } catch (error) {
    console.error('Failed to load bots:', error)
    alert('Failed to load bots')
  }
}

const loadDatasets = async () => {
  try {
    const response = await getDatasets()
    datasets.value = response.data
  } catch (error) {
    console.error('Failed to load datasets:', error)
  }
}

const loadChorusModels = async () => {
  try {
    const response = await getChorusModels()
    chorusModels.value = response.data
  } catch (error) {
    console.error('Failed to load Chorus models:', error)
  }
}

const createBotHandler = async () => {
  if (!newBot.value.name) {
    alert('Please enter a bot name')
    return
  }

  if (!newBot.value.instructions) {
    alert('Please enter bot instructions')
    return
  }

  if (!newBot.value.chorus_model_id) {
    alert('Please select a Chorus model')
    return
  }

  try {
    await createBot(newBot.value)
    showCreateModal.value = false
    newBot.value = {
      name: '',
      instructions: '',
      dataset_id: null,
      chorus_model_id: null,
      rag_results_count: 5
    }
    loadBots()
  } catch (error) {
    console.error('Failed to create bot:', error)
    alert('Failed to create bot')
  }
}

const deleteBotHandler = async (botId) => {
  if (!confirm('Are you sure you want to delete this bot?')) return

  try {
    await deleteBot(botId)
    loadBots()
  } catch (error) {
    console.error('Failed to delete bot:', error)
    alert('Failed to delete bot')
  }
}

const navigateToChat = (botId) => {
  router.push(`/chat/${botId}`)
}

const getDatasetName = (datasetId) => {
  const dataset = datasets.value.find(d => d.id === datasetId)
  return dataset ? dataset.name : 'No dataset'
}

const getChorusModelName = (modelId) => {
  const model = chorusModels.value.find(m => m.id === modelId)
  return model ? model.name : 'No model'
}

onMounted(() => {
  loadBots()
  loadDatasets()
  loadChorusModels()
})
</script>

