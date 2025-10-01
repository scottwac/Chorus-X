<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-800">Chorus Models</h1>
        <p class="text-gray-600 mt-1">Configure multi-LLM orchestration with voting</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="px-6 py-3 bg-chorus-green-600 text-white rounded-lg hover:bg-chorus-green-700 shadow-lg font-medium"
      >
        + New Chorus Model
      </button>
    </div>

    <!-- Models Grid -->
    <div v-if="chorusModels.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div
        v-for="model in chorusModels"
        :key="model.id"
        class="bg-white rounded-xl shadow-md hover:shadow-xl p-6 border-2 border-transparent hover:border-chorus-green-300"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h3 class="text-xl font-bold text-gray-800">{{ model.name }}</h3>
            <p class="text-sm text-gray-600 mt-1">{{ model.description || 'No description' }}</p>
          </div>
          <button
            @click="deleteChorusModelHandler(model.id)"
            class="text-red-500 hover:text-red-700 text-xl"
          >
            🗑️
          </button>
        </div>

        <!-- Responders -->
        <div class="mb-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">🎤 Responders ({{ model.responder_llms.length }})</h4>
          <div class="space-y-1">
            <div
              v-for="(llm, idx) in model.responder_llms"
              :key="idx"
              class="text-sm bg-blue-50 text-blue-700 px-3 py-1 rounded-full inline-block mr-2"
            >
              {{ llm.provider }} / {{ llm.model }}
            </div>
          </div>
        </div>

        <!-- Evaluators -->
        <div>
          <h4 class="text-sm font-semibold text-gray-700 mb-2">⚖️ Evaluators ({{ model.evaluator_llms.length }})</h4>
          <div class="space-y-1">
            <div
              v-for="(llm, idx) in model.evaluator_llms"
              :key="idx"
              class="text-sm bg-green-50 text-green-700 px-3 py-1 rounded-full inline-block mr-2"
            >
              {{ llm.provider }} / {{ llm.model }}
            </div>
          </div>
        </div>

        <div class="text-xs text-gray-500 mt-4">
          Created {{ new Date(model.created_at).toLocaleDateString() }}
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-16 bg-white rounded-xl shadow-md">
      <div class="text-6xl mb-4">🎭</div>
      <h3 class="text-xl font-semibold text-gray-800 mb-2">No Chorus models yet</h3>
      <p class="text-gray-600 mb-6">Create your first Chorus model to orchestrate multiple LLMs</p>
      <button
        @click="showCreateModal = true"
        class="px-6 py-3 bg-chorus-green-600 text-white rounded-lg hover:bg-chorus-green-700 font-medium"
      >
        Create Chorus Model
      </button>
    </div>

    <!-- Create Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-3xl my-8 max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Create Chorus Model</h2>
        
        <div class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Model Name</label>
            <input
              v-model="newModel.name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chorus-green-500 focus:border-transparent"
              placeholder="My Chorus Model"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Description (Optional)</label>
            <textarea
              v-model="newModel.description"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chorus-green-500 focus:border-transparent"
              rows="2"
              placeholder="Describe your Chorus model..."
            ></textarea>
          </div>

          <!-- Responder LLMs -->
          <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-3">🎤 Responder LLMs</h3>
            <p class="text-sm text-gray-600 mb-3">These LLMs will generate responses to user queries</p>
            
            <div v-for="(llm, idx) in newModel.responder_llms" :key="idx" class="flex gap-2 mb-2">
              <select
                v-model="llm.provider"
                class="px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="groq">Groq</option>
              </select>
              
              <select
                v-model="llm.model"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option v-for="model in getModelsForProvider(llm.provider)" :key="model" :value="model">
                  {{ model }}
                </option>
              </select>
              
              <button
                @click="newModel.responder_llms.splice(idx, 1)"
                class="px-3 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
              >
                Remove
              </button>
            </div>
            
            <button
              @click="addResponder"
              class="mt-2 px-4 py-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200"
            >
              + Add Responder
            </button>
          </div>

          <!-- Evaluator LLMs -->
          <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-3">⚖️ Evaluator LLMs</h3>
            <p class="text-sm text-gray-600 mb-3">These LLMs will vote on which response is best</p>
            
            <div v-for="(llm, idx) in newModel.evaluator_llms" :key="idx" class="flex gap-2 mb-2">
              <select
                v-model="llm.provider"
                class="px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="groq">Groq</option>
              </select>
              
              <select
                v-model="llm.model"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option v-for="model in getModelsForProvider(llm.provider)" :key="model" :value="model">
                  {{ model }}
                </option>
              </select>
              
              <button
                @click="newModel.evaluator_llms.splice(idx, 1)"
                class="px-3 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
              >
                Remove
              </button>
            </div>
            
            <button
              @click="addEvaluator"
              class="mt-2 px-4 py-2 bg-green-100 text-green-600 rounded-lg hover:bg-green-200"
            >
              + Add Evaluator
            </button>
          </div>
        </div>

        <div class="flex space-x-4 mt-8">
          <button
            @click="showCreateModal = false"
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="createChorusModelHandler"
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
import { getChorusModels, createChorusModel, deleteChorusModel } from '../api'

const chorusModels = ref([])
const showCreateModal = ref(false)
const newModel = ref({
  name: '',
  description: '',
  responder_llms: [{ provider: 'openai', model: 'gpt-5-2025-08-07' }],
  evaluator_llms: [{ provider: 'anthropic', model: 'claude-3-7-sonnet-20250219' }]
})

const modelsByProvider = {
  openai: [
    'gpt-5-2025-08-07',
    'gpt-5-nano',
    'gpt-5-nano-2025-08-07',
    'gpt-4o',
    'gpt-4o-mini',
    'gpt-4-turbo',
    'gpt-4',
    'gpt-3.5-turbo'
  ],
  anthropic: [
    'claude-3-7-sonnet-20250219',
    'claude-3-5-sonnet-20241022',
    'claude-3-5-sonnet-20240620',
    'claude-3-5-haiku-20241022',
    'claude-3-opus-20240229',
    'claude-3-sonnet-20240229',
    'claude-3-haiku-20240307'
  ],
  groq: [
    'llama-3.3-70b-versatile',
    'llama-3.1-70b-versatile',
    'llama-3.1-8b-instant',
    'mixtral-8x7b-32768',
    'gemma2-9b-it'
  ]
}

const getModelsForProvider = (provider) => {
  return modelsByProvider[provider] || []
}

const loadChorusModels = async () => {
  try {
    const response = await getChorusModels()
    chorusModels.value = response.data
  } catch (error) {
    console.error('Failed to load Chorus models:', error)
    alert('Failed to load Chorus models')
  }
}

const createChorusModelHandler = async () => {
  if (!newModel.value.name) {
    alert('Please enter a model name')
    return
  }

  if (newModel.value.responder_llms.length === 0) {
    alert('Please add at least one responder LLM')
    return
  }

  if (newModel.value.evaluator_llms.length === 0 && newModel.value.responder_llms.length > 1) {
    alert('Please add at least one evaluator LLM when using multiple responders')
    return
  }

  try {
    await createChorusModel(newModel.value)
    showCreateModal.value = false
    newModel.value = {
      name: '',
      description: '',
      responder_llms: [{ provider: 'openai', model: 'gpt-5-2025-08-07' }],
      evaluator_llms: [{ provider: 'anthropic', model: 'claude-3-7-sonnet-20250219' }]
    }
    loadChorusModels()
  } catch (error) {
    console.error('Failed to create Chorus model:', error)
    alert('Failed to create Chorus model')
  }
}

const deleteChorusModelHandler = async (modelId) => {
  if (!confirm('Are you sure you want to delete this Chorus model?')) return

  try {
    await deleteChorusModel(modelId)
    loadChorusModels()
  } catch (error) {
    console.error('Failed to delete Chorus model:', error)
    alert('Failed to delete Chorus model')
  }
}

const addResponder = () => {
  newModel.value.responder_llms.push({ provider: 'openai', model: 'gpt-5-2025-08-07' })
}

const addEvaluator = () => {
  newModel.value.evaluator_llms.push({ provider: 'anthropic', model: 'claude-3-7-sonnet-20250219' })
}

onMounted(() => {
  loadChorusModels()
})
</script>

