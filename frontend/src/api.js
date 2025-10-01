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
export const uploadFiles = (datasetId, files) => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  return api.post(`/datasets/${datasetId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export const deleteDataset = (datasetId) => api.delete(`/datasets/${datasetId}`)
export const getFileContent = (datasetId, fileId) => api.get(`/datasets/${datasetId}/files/${fileId}`)
export const getFileImage = (datasetId, fileId) => `${API_BASE_URL}/datasets/${datasetId}/files/${fileId}/image`
export const deleteFile = (datasetId, fileId) => api.delete(`/datasets/${datasetId}/files/${fileId}`)

// Chorus Models
export const getChorusModels = () => api.get('/chorus-models')
export const createChorusModel = (data) => api.post('/chorus-models', data)
export const deleteChorusModel = (modelId) => api.delete(`/chorus-models/${modelId}`)

// Bots
export const getBots = () => api.get('/bots')
export const createBot = (data) => api.post('/bots', data)
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

