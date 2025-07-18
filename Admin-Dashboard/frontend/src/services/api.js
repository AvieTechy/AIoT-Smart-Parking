import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: import.meta.env.VITE_API_TIMEOUT || 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const apiService = {
  // Health check
  async healthCheck() {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      throw new Error('Failed to connect to backend')
    }
  },

  // Session endpoints
  async getSessions(gate = null, limit = 100) {
    try {
      const params = { limit }
      if (gate) params.gate = gate
      
      const response = await api.get('/api/sessions', { params })
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch sessions')
    }
  },

  async getGroupedSessions() {
    try {
      const response = await api.get('/api/sessions/grouped')
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch grouped sessions')
    }
  },

  async getSession(sessionId) {
    try {
      const response = await api.get(`/api/sessions/${sessionId}`)
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch session details')
    }
  },

  async getCurrentVehicleCount() {
    try {
      const response = await api.get('/api/sessions/current-vehicle-count')
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch current vehicle count')
    }
  },

  // Parking slots endpoints
  async getParkingSlots() {
    try {
      const response = await api.get('/api/parking/slots')
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch parking slots')
    }
  },

  async getAvailableSlots() {
    try {
      const response = await api.get('/api/parking/slots/available')
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch available slots')
    }
  },

  async getOccupiedSlots() {
    try {
      const response = await api.get('/api/parking/slots/occupied')
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch occupied slots')
    }
  }
}

export default api
