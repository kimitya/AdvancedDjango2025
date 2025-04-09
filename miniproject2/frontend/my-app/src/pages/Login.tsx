// src/pages/Login.tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../services/api'
import toast from 'react-hot-toast'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      const response = await login({ username, password })
      console.log('Login response:', response.data)
      localStorage.setItem('token', response.data.access)
      toast.success('Successfully logged in!')
      navigate('/')
    } catch (error: any) {
      console.error('Login error:', error.response?.data || error.message)
      setError(
        error.response?.data?.detail || 
        error.message || 
        'Failed to login. Please check your credentials and try again.'
      )
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-4 text-gray-800">Login</h1>
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              className="w-full p-2 border rounded"
            />
          </div>
          <div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full p-2 border rounded"
            />
          </div>
          <button 
            type="submit" 
            className="submit-button w-full bg-teal-500 text-white p-2 rounded hover:bg-teal-600 transition-colors"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  )
}