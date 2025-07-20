import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  TrendingUp, 
  FileText, 
  Users, 
  DollarSign,
  Activity,
  Calendar,
  Download,
  Plus,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '../contexts/AuthContext'
import { Link } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'

const Dashboard = () => {
  const { user, API_BASE_URL } = useAuth()
  const [stats, setStats] = useState(null)
  const [recentModels, setRecentModels] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Récupérer les statistiques utilisateur
      const [modelsResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/financial/models/user`, {
          credentials: 'include'
        })
      ])

      if (modelsResponse.ok) {
        const modelsData = await modelsResponse.json()
        setRecentModels(modelsData.models.slice(0, 5)) // 5 derniers modèles
        
        // Calculer les statistiques
        const totalModels = modelsData.models.length
        const thisMonth = modelsData.models.filter(model => {
          const modelDate = new Date(model.created_at)
          const now = new Date()
          return modelDate.getMonth() === now.getMonth() && modelDate.getFullYear() === now.getFullYear()
        }).length

        setStats({
          totalModels,
          thisMonth,
          exportsUsed: user?.free_exports_used || 0,
          exportsRemaining: user?.account_status === 'demo' ? 3 - (user?.free_exports_used || 0) : 'Illimité'
        })
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setLoading(false)
    }
  }

  const getModelTypeLabel = (type) => {
    const labels = {
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
    return labels[type] || type
  }

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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Bonjour, {user?.username} 👋
          </h1>
          <p className="text-gray-600">
            Voici un aperçu de votre activité de modélisation financière
          </p>
        </motion.div>

        {/* Statistiques principales */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Modèles créés
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.totalModels || 0}</div>
              <p className="text-xs text-muted-foreground">
                +{stats?.thisMonth || 0} ce mois
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Exports utilisés
              </CardTitle>
              <Download className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.exportsUsed || 0}</div>
              <p className="text-xs text-muted-foreground">
                {typeof stats?.exportsRemaining === 'number' 
                  ? `${stats.exportsRemaining} restants`
                  : 'Illimité'
                }
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Statut du compte
              </CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold capitalize">
                {user?.account_status?.replace('_', ' ') || 'Demo'}
              </div>
              <p className="text-xs text-muted-foreground">
                {user?.account_status === 'demo' ? 'Essai gratuit' : 'Abonnement actif'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Membre depuis
              </CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {user?.created_at ? formatDate(user.created_at) : 'N/A'}
              </div>
              <p className="text-xs text-muted-foreground">
                Date d'inscription
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Actions rapides */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Actions rapides</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link to="/models">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-blue-100 rounded-lg">
                      <BarChart3 className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">Nouveau modèle</h3>
                      <p className="text-sm text-gray-600">Créer une analyse financière</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link to="/statements">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-green-100 rounded-lg">
                      <FileText className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">États financiers</h3>
                      <p className="text-sm text-gray-600">Générer depuis une balance</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Analyse IA</h3>
                    <p className="text-sm text-gray-600">Insights intelligents</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>

        {/* Modèles récents */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Modèles récents</h2>
            <Link to="/models">
              <Button variant="outline" size="sm">
                Voir tout
                <ArrowUpRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>

          {recentModels.length > 0 ? (
            <Card>
              <CardContent className="p-0">
                <div className="divide-y divide-gray-200">
                  {recentModels.map((model, index) => (
                    <motion.div
                      key={model.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 * index }}
                      className="p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-blue-100 rounded-lg">
                            <BarChart3 className="h-4 w-4 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-900">{model.name}</h3>
                            <p className="text-sm text-gray-600">
                              {getModelTypeLabel(model.model_type)}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-900">
                            {formatDate(model.created_at)}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(model.created_at).toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Aucun modèle créé
                </h3>
                <p className="text-gray-600 mb-4">
                  Commencez par créer votre premier modèle financier
                </p>
                <Link to="/models">
                  <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Créer un modèle
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </motion.div>

        {/* Upgrade prompt pour les comptes démo */}
        {user?.account_status === 'demo' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mb-8"
          >
            <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-blue-900 mb-2">
                      Passez à un abonnement premium
                    </h3>
                    <p className="text-blue-700 mb-4">
                      Débloquez les exports illimités et toutes les fonctionnalités avancées
                    </p>
                    <div className="flex space-x-4">
                      <a 
                        href="https://me.fedapay.com/fincashmonthly" 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        <Button size="sm">
                          Mensuel - 30,000 FCFA
                        </Button>
                      </a>
                      <a 
                        href="https://me.fedapay.com/fincashannually" 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        <Button variant="outline" size="sm">
                          Annuel - 200,000 FCFA
                        </Button>
                      </a>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">
                      {3 - (user?.free_exports_used || 0)}
                    </div>
                    <div className="text-sm text-blue-700">
                      exports restants
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default Dashboard

