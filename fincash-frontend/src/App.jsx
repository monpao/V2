import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import './App.css'

// Pages
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Dashboard from './pages/Dashboard'
import ModelsPage from './pages/ModelsPage'
import StatementsPage from './pages/StatementsPage'
import AdminPage from './pages/AdminPage'

// Context
import { AuthProvider, useAuth } from './contexts/AuthContext'

// Components
import LoadingSpinner from './components/LoadingSpinner'
import Navbar from './components/Navbar'

function AppContent() {
  const { user, loading } = useAuth()
  const [isInitialized, setIsInitialized] = useState(false)

  useEffect(() => {
    // Simuler l'initialisation de l'app
    const timer = setTimeout(() => {
      setIsInitialized(true)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  if (loading || !isInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="mb-8">
            <div className="text-4xl font-bold text-blue-600 mb-2">Fincash</div>
            <div className="text-gray-600">Modélisation Financière Professionnelle</div>
          </div>
          <LoadingSpinner size="lg" />
        </motion.div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route 
              path="/login" 
              element={user ? <Navigate to="/dashboard" /> : <LoginPage />} 
            />
            <Route 
              path="/register" 
              element={user ? <Navigate to="/dashboard" /> : <RegisterPage />} 
            />
            <Route 
              path="/dashboard" 
              element={user ? <><Navbar /><Dashboard /></> : <Navigate to="/login" />} 
            />
            <Route 
              path="/models" 
              element={user ? <><Navbar /><ModelsPage /></> : <Navigate to="/login" />} 
            />
            <Route 
              path="/statements" 
              element={user ? <><Navbar /><StatementsPage /></> : <Navigate to="/login" />} 
            />
            <Route 
              path="/admin" 
              element={user?.role === 'admin' ? <><Navbar /><AdminPage /></> : <Navigate to="/dashboard" />} 
            />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </AnimatePresence>
      </div>
    </Router>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App

