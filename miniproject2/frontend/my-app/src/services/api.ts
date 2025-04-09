// src/services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    console.log('Adding Authorization header with token:', token) // Debug
  } else {
    console.log('No token found in localStorage') // Debug
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// Rest of the file remains unchanged...
export const login = (credentials: { username: string; password: string }) =>
  api.post('login/', credentials)

export const register = (data: { username: string; email: string; password: string; role: string }) =>
  api.post('register/', data)

export const uploadResume = (formData: FormData) =>
  api.post('resumes/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

export const replaceResume = (formData: FormData) =>
  api.put('resumes/replace/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

export const createJob = (data: { description: string }) =>
  api.post('resumes/jobs/create/', data)

export const getJobs = () =>
  api.get('resumes/jobs/')

export const getJobDetail = (jobId: string) =>
  api.get(`resumes/jobs/${jobId}/`)

export const getJobMatches = (jobId: string) =>
  api.get(`resumes/jobs/${jobId}/matches/`)