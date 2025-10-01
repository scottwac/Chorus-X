<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-800">Datasets</h1>
        <p class="text-gray-600 mt-1">Create and manage vector stores for your knowledge base</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="px-6 py-3 bg-chorus-green-600 text-white rounded-lg hover:bg-chorus-green-700 shadow-lg font-medium"
      >
        + New Dataset
      </button>
    </div>

    <!-- Datasets Grid -->
    <div v-if="datasets.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="dataset in datasets"
        :key="dataset.id"
        class="bg-white rounded-xl shadow-md hover:shadow-xl p-6 border-2 border-transparent hover:border-chorus-green-300"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h3 class="text-xl font-bold text-gray-800">{{ dataset.name }}</h3>
            <p class="text-sm text-gray-600 mt-1">{{ dataset.description || 'No description' }}</p>
          </div>
          <button
            @click="deleteDatasetHandler(dataset.id)"
            class="text-red-500 hover:text-red-700 text-xl"
          >
            🗑️
          </button>
        </div>

        <div class="flex items-center justify-between text-sm text-gray-500 mb-4">
          <button
            @click="viewDatasetFiles(dataset.id)"
            class="flex items-center gap-1 hover:text-chorus-green-600 hover:underline"
          >
            📄 {{ dataset.file_count }} files
          </button>
          <span>{{ new Date(dataset.created_at).toLocaleDateString() }}</span>
        </div>

        <!-- File Upload Area -->
        <div
          @drop.prevent="handleDrop($event, dataset.id)"
          @dragover.prevent
          @dragenter="dragEnter"
          @dragleave="dragLeave"
          :class="dragActive ? 'border-chorus-green-500 bg-chorus-green-50' : 'border-gray-300 bg-gray-50'"
          class="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:bg-chorus-green-50 hover:border-chorus-green-400"
          @click="triggerFileInput(dataset.id)"
        >
          <input
            type="file"
            :ref="`fileInput-${dataset.id}`"
            @change="handleFileSelect($event, dataset.id)"
            multiple
            accept=".txt,.pdf,.docx,.md,.png,.jpg,.jpeg,.gif,.bmp,.webp"
            class="hidden"
          />
          <div class="text-4xl mb-2">📤</div>
          <p class="text-sm text-gray-600">Drop files here or click to upload</p>
          <p class="text-xs text-gray-500 mt-1">Supports: Text, PDF, DOCX, MD, Images</p>
        </div>

        <!-- Upload Progress -->
        <div v-if="uploadingDatasets[dataset.id]" class="mt-4">
          <div class="flex items-center justify-center space-x-2">
            <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-chorus-green-600"></div>
            <span class="text-sm text-gray-600">Processing files...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-16 bg-white rounded-xl shadow-md">
      <div class="text-6xl mb-4">📁</div>
      <h3 class="text-xl font-semibold text-gray-800 mb-2">No datasets yet</h3>
      <p class="text-gray-600 mb-6">Create your first dataset to get started</p>
      <button
        @click="showCreateModal = true"
        class="px-6 py-3 bg-chorus-green-600 text-white rounded-lg hover:bg-chorus-green-700 font-medium"
      >
        Create Dataset
      </button>
    </div>

    <!-- Create Dataset Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Create New Dataset</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Dataset Name</label>
            <input
              v-model="newDataset.name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chorus-green-500 focus:border-transparent"
              placeholder="My Knowledge Base"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Description (Optional)</label>
            <textarea
              v-model="newDataset.description"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chorus-green-500 focus:border-transparent"
              rows="3"
              placeholder="Describe your dataset..."
            ></textarea>
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
            @click="createDatasetHandler"
            class="flex-1 px-4 py-2 bg-chorus-green-600 text-white rounded-lg hover:bg-chorus-green-700"
          >
            Create
          </button>
        </div>
      </div>
    </div>

    <!-- Dataset Files Modal -->
    <div
      v-if="showFilesModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showFilesModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-gray-800">Files in {{ selectedDataset?.name }}</h2>
          <button @click="showFilesModal = false" class="text-2xl text-gray-500 hover:text-gray-700">×</button>
        </div>
        
        <div v-if="datasetFiles.length > 0" class="space-y-2">
          <div
            v-for="file in datasetFiles"
            :key="file.id"
            class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
            @click="viewFile(file.id)"
          >
            <div class="flex-1">
              <div class="font-semibold text-gray-800">{{ file.filename }}</div>
              <div class="text-sm text-gray-600">
                {{ file.file_type }} • {{ formatFileSize(file.file_size) }} • {{ file.chunks_count }} chunks
              </div>
            </div>
            <button
              @click.stop="deleteFileHandler(file.id)"
              class="text-red-500 hover:text-red-700 px-3 py-1 rounded"
            >
              🗑️
            </button>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          No files in this dataset yet
        </div>
      </div>
    </div>

    <!-- File Content Modal -->
    <div
      v-if="showFileContent"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showFileContent = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-6xl max-h-[80vh] flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold text-gray-800">{{ currentFile?.filename }}</h2>
          <button @click="showFileContent = false" class="text-2xl text-gray-500 hover:text-gray-700">×</button>
        </div>
        
        <div class="text-sm text-gray-600 mb-4">
          {{ currentFile?.file_type }} • {{ formatFileSize(currentFile?.file_size) }} • {{ currentFile?.chunks_count }} chunks
        </div>
        
        <div class="flex-1 overflow-y-auto bg-gray-50 rounded-lg p-4">
          <pre class="whitespace-pre-wrap text-sm text-gray-800">{{ currentFile?.content }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDatasets, getDataset, createDataset, uploadFiles, deleteDataset, getFileContent, deleteFile } from '../api'

const datasets = ref([])
const showCreateModal = ref(false)
const showFilesModal = ref(false)
const showFileContent = ref(false)
const newDataset = ref({ name: '', description: '' })
const dragActive = ref(false)
const uploadingDatasets = ref({})
const selectedDataset = ref(null)
const datasetFiles = ref([])
const currentFile = ref(null)

const loadDatasets = async () => {
  try {
    const response = await getDatasets()
    datasets.value = response.data
  } catch (error) {
    console.error('Failed to load datasets:', error)
    alert('Failed to load datasets')
  }
}

const createDatasetHandler = async () => {
  if (!newDataset.value.name) {
    alert('Please enter a dataset name')
    return
  }

  try {
    await createDataset(newDataset.value)
    showCreateModal.value = false
    newDataset.value = { name: '', description: '' }
    loadDatasets()
  } catch (error) {
    console.error('Failed to create dataset:', error)
    alert('Failed to create dataset')
  }
}

const deleteDatasetHandler = async (datasetId) => {
  if (!confirm('Are you sure you want to delete this dataset?')) return

  try {
    await deleteDataset(datasetId)
    loadDatasets()
  } catch (error) {
    console.error('Failed to delete dataset:', error)
    alert('Failed to delete dataset')
  }
}

const handleDrop = async (event, datasetId) => {
  dragActive.value = false
  const files = Array.from(event.dataTransfer.files)
  await uploadFilesToDataset(datasetId, files)
}

const triggerFileInput = (datasetId) => {
  const input = document.querySelector(`input[ref="fileInput-${datasetId}"]`)
  if (input) input.click()
}

const handleFileSelect = async (event, datasetId) => {
  const files = Array.from(event.target.files)
  await uploadFilesToDataset(datasetId, files)
}

const uploadFilesToDataset = async (datasetId, files) => {
  if (files.length === 0) return

  uploadingDatasets.value[datasetId] = true

  try {
    await uploadFiles(datasetId, files)
    loadDatasets()
  } catch (error) {
    console.error('Failed to upload files:', error)
    alert('Failed to upload files')
  } finally {
    uploadingDatasets.value[datasetId] = false
  }
}

const dragEnter = () => {
  dragActive.value = true
}

const dragLeave = () => {
  dragActive.value = false
}

const viewDatasetFiles = async (datasetId) => {
  try {
    const response = await getDataset(datasetId)
    selectedDataset.value = response.data
    datasetFiles.value = response.data.files || []
    showFilesModal.value = true
  } catch (error) {
    console.error('Failed to load dataset files:', error)
    alert('Failed to load dataset files')
  }
}

const viewFile = async (fileId) => {
  try {
    const response = await getFileContent(selectedDataset.value.id, fileId)
    currentFile.value = response.data
    showFileContent.value = true
  } catch (error) {
    console.error('Failed to load file content:', error)
    alert('Failed to load file content')
  }
}

const deleteFileHandler = async (fileId) => {
  if (!confirm('Are you sure you want to delete this file?')) return

  try {
    await deleteFile(selectedDataset.value.id, fileId)
    // Reload files
    viewDatasetFiles(selectedDataset.value.id)
    loadDatasets() // Refresh file count
  } catch (error) {
    console.error('Failed to delete file:', error)
    alert('Failed to delete file')
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

onMounted(() => {
  loadDatasets()
})
</script>

