import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  Plus, 
  Search, 
  Filter,
  Download,
  Eye,
  Trash2,
  Calendar,
  TrendingUp
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'

const ModelsPage = () => {
  const { user, API_BASE_URL } = useAuth()
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState('all')

  const modelTypes = {
    'all': 'Tous les modèles',
    'dcf': 'DCF',
    'investment_budgeting': 'Budget d\'investissement',
    'loan_amortization': 'Amortissement de prêt',
    'bond_pricing': 'Évaluation d\'obligations',
    'black_scholes': 'Black-Scholes',
    'financial_ratios': 'Ratios financiers',
    'real_estate_valuation': 'Évaluation immobilière',
    'lbo_analysis': 'Analyse LBO',
    'merger_analysis': 'Analyse M&A'
  }

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/financial/models/user`, {
        credentials: 'include'
      })

      if (response.ok) {
        const data = await response.json()
        setModels(data.models)
      }
    } catch (error) {
      console.error('Erreur lors du chargement des modèles:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredModels = models.filter(model => {
    const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = selectedType === 'all' || model.model_type === selectedType
    return matchesSearch && matchesType
  })

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 pt-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* En-tête */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Modèles Financiers
              </h1>
              <p className="text-gray-600">
                Créez et gérez vos analyses financières professionnelles
              </p>
            </div>
            <Button className="flex items-center space-x-2">
              <Plus size={20} />
              <span>Nouveau modèle</span>
            </Button>
          </div>
        </motion.div>

        {/* Filtres et recherche */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                    <Input
                      placeholder="Rechercher un modèle..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="md:w-64">
                  <select
                    value={selectedType}
                    onChange={(e) => setSelectedType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {Object.entries(modelTypes).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Liste des modèles */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {filteredModels.length > 0 ? (
            <div className="grid gap-6">
              {filteredModels.map((model, index) => (
                <motion.div
                  key={model.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <Card className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="p-3 bg-blue-100 rounded-lg">
                            <BarChart3 className="h-6 w-6 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {model.name}
                            </h3>
                            <p className="text-sm text-gray-600 mb-2">
                              {model.description}
                            </p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              <span className="flex items-center">
                                <Calendar size={14} className="mr-1" />
                                {formatDate(model.created_at)}
                              </span>
                              <span className="px-2 py-1 bg-gray-100 rounded-full">
                                {modelTypes[model.model_type]}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye size={16} className="mr-1" />
                            Voir
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download size={16} className="mr-1" />
                            Export
                          </Button>
                          <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                            <Trash2 size={16} />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {searchTerm || selectedType !== 'all' ? 'Aucun modèle trouvé' : 'Aucun modèle créé'}
                </h3>
                <p className="text-gray-600 mb-6">
                  {searchTerm || selectedType !== 'all' 
                    ? 'Essayez de modifier vos critères de recherche'
                    : 'Commencez par créer votre premier modèle financier'
                  }
                </p>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Créer un modèle
                </Button>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default ModelsPage

