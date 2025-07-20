import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Eye, EyeOff, Mail, Lock, User, ArrowLeft, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [acceptTerms, setAcceptTerms] = useState(false)

  const { register } = useAuth()
  const navigate = useNavigate()

  const validatePassword = (password) => {
    const minLength = password.length >= 8
    const hasUpper = /[A-Z]/.test(password)
    const hasLower = /[a-z]/.test(password)
    const hasNumber = /\d/.test(password)
    
    return {
      minLength,
      hasUpper,
      hasLower,
      hasNumber,
      isValid: minLength && hasUpper && hasLower && hasNumber
    }
  }

  const passwordValidation = validatePassword(formData.password)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    // Validations côté client
    if (!acceptTerms) {
      setError('Vous devez accepter les conditions d\'utilisation')
      setLoading(false)
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      setLoading(false)
      return
    }

    if (!passwordValidation.isValid) {
      setError('Le mot de passe ne respecte pas les critères de sécurité')
      setLoading(false)
      return
    }

    try {
      const result = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password
      })
      
      if (result.success) {
        navigate('/dashboard')
      } else {
        setError(result.error)
      }
    } catch (err) {
      setError('Une erreur inattendue s\'est produite')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-md w-full space-y-8"
      >
        {/* Header */}
        <div className="text-center">
          <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-6">
            <ArrowLeft size={20} className="mr-2" />
            Retour à l'accueil
          </Link>
          
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5 }}
            className="text-4xl font-bold text-blue-600 mb-2"
          >
            Fincash
          </motion.div>
          
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Créer un compte
          </h2>
          <p className="text-gray-600">
            Commencez votre essai gratuit dès maintenant
          </p>
        </div>

        {/* Avantages de l'inscription */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="bg-blue-50 rounded-lg p-4"
        >
          <div className="flex items-center justify-center space-x-6 text-sm text-blue-700">
            <div className="flex items-center">
              <CheckCircle size={16} className="mr-1" />
              <span>3 exports gratuits</span>
            </div>
            <div className="flex items-center">
              <CheckCircle size={16} className="mr-1" />
              <span>Tous les modèles</span>
            </div>
            <div className="flex items-center">
              <CheckCircle size={16} className="mr-1" />
              <span>Analyses IA</span>
            </div>
          </div>
        </motion.div>

        {/* Formulaire */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-white rounded-lg shadow-lg p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md"
              >
                {error}
              </motion.div>
            )}

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Nom d'utilisateur
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="pl-10"
                  placeholder="Choisissez un nom d'utilisateur"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Adresse email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="pl-10"
                  placeholder="votre@email.com"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="pl-10 pr-10"
                  placeholder="Créez un mot de passe sécurisé"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              
              {/* Indicateurs de force du mot de passe */}
              {formData.password && (
                <div className="mt-2 space-y-1">
                  <div className="flex space-x-1">
                    <div className={`h-1 w-1/4 rounded ${passwordValidation.minLength ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                    <div className={`h-1 w-1/4 rounded ${passwordValidation.hasLower ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                    <div className={`h-1 w-1/4 rounded ${passwordValidation.hasUpper ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                    <div className={`h-1 w-1/4 rounded ${passwordValidation.hasNumber ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                  </div>
                  <div className="text-xs text-gray-600 space-y-1">
                    <div className={passwordValidation.minLength ? 'text-green-600' : 'text-gray-500'}>
                      ✓ Au moins 8 caractères
                    </div>
                    <div className={passwordValidation.hasUpper ? 'text-green-600' : 'text-gray-500'}>
                      ✓ Une majuscule
                    </div>
                    <div className={passwordValidation.hasLower ? 'text-green-600' : 'text-gray-500'}>
                      ✓ Une minuscule
                    </div>
                    <div className={passwordValidation.hasNumber ? 'text-green-600' : 'text-gray-500'}>
                      ✓ Un chiffre
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirmer le mot de passe
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="pl-10 pr-10"
                  placeholder="Confirmez votre mot de passe"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              {formData.confirmPassword && formData.password !== formData.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">
                  Les mots de passe ne correspondent pas
                </p>
              )}
            </div>

            <div className="flex items-center">
              <input
                id="accept-terms"
                name="accept-terms"
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="accept-terms" className="ml-2 block text-sm text-gray-700">
                J'accepte les{' '}
                <a href="#" className="text-blue-600 hover:text-blue-500">
                  conditions d'utilisation
                </a>{' '}
                et la{' '}
                <a href="#" className="text-blue-600 hover:text-blue-500">
                  politique de confidentialité
                </a>
              </label>
            </div>

            <Button
              type="submit"
              disabled={loading || !acceptTerms || !passwordValidation.isValid}
              className="w-full flex justify-center items-center"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Création du compte...
                </>
              ) : (
                'Créer mon compte gratuit'
              )}
            </Button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Déjà un compte ?</span>
              </div>
            </div>

            <div className="mt-6 text-center">
              <Link
                to="/login"
                className="text-blue-600 hover:text-blue-500 font-medium"
              >
                Se connecter
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Sécurité et confidentialité */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center text-sm text-gray-600"
        >
          <p>
            🔒 Vos données sont sécurisées et chiffrées. 
            Nous ne partageons jamais vos informations personnelles.
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
}

export default RegisterPage

