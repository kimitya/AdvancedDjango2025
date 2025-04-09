// src/App.tsx
import { Outlet } from 'react-router-dom'
import Navbar from './components/Navbar'

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <Outlet /> {/* Remove container classes to allow full-width children */}
    </div>
  )
}

export default App