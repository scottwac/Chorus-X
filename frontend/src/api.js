import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Datasets
export const getDatasets = () => api.get('/datasets')
export const getDataset = (datasetId) => api.get(`/datasets/${datasetId}`)
export const createDataset = (data) => api.post('/datasets', data)
export const uploadFiles = async (datasetId, files, onProgress) => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  
  // Use fetch with streaming for real-time progress updates
  const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}/upload`, {
    method: 'POST',
    body: formData
  })
  
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let finalResult = null
  
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    
    buffer += decoder.decode(value, { stream: true })
    
    // Split by double newlines (SSE format)
    const lines = buffer.split('\n\n')
    buffer = lines.pop() // Keep incomplete message in buffer
    
    for (const line of lines) {
      if (!line.trim()) continue
      
      // Parse SSE format: "event: type\ndata: {...}"
      const eventMatch = line.match(/event: (\w+)\ndata: (.+)/)
      if (eventMatch) {
        const [_, eventType, dataStr] = eventMatch
        const data = JSON.parse(dataStr)
        
        if (eventType === 'status' && onProgress) {
          onProgress(data)
        } else if (eventType === 'final') {
          finalResult = data
        } else if (eventType === 'error') {
          throw new Error(data.message)
        }
      }
    }
  }
  
  return { data: finalResult }
}
export const deleteDataset = (datasetId) => api.delete(`/datasets/${datasetId}`)
export const getFileContent = (datasetId, fileId) => api.get(`/datasets/${datasetId}/files/${fileId}`)
export const getFileImage = (datasetId, fileId) => `${API_BASE_URL}/datasets/${datasetId}/files/${fileId}/image`
export const deleteFile = (datasetId, fileId) => api.delete(`/datasets/${datasetId}/files/${fileId}`)

// Chorus Models
export const getChorusModels = () => api.get('/chorus-models')
export const createChorusModel = (data) => api.post('/chorus-models', data)
export const updateChorusModel = (modelId, data) => api.put(`/chorus-models/${modelId}`, data)
export const deleteChorusModel = (modelId) => api.delete(`/chorus-models/${modelId}`)

// Bots
export const getBots = () => api.get('/bots')
export const createBot = (data) => api.post('/bots', data)
export const updateBot = (botId, data) => api.put(`/bots/${botId}`, data)
export const deleteBot = (botId) => api.delete(`/bots/${botId}`)
export const chatWithBot = (botId, message, ragCount = null, imageSettings = null) => {
  const payload = { message }
  if (ragCount !== null) {
    payload.rag_count = ragCount
  }
  if (imageSettings !== null) {
    payload.image_settings = imageSettings
  }
  return api.post(`/bots/${botId}/chat`, payload)
}
export const getChatHistory = (botId) => api.get(`/bots/${botId}/history`)

// Health Check
export const checkHealth = () => api.get('/health')

export default api

