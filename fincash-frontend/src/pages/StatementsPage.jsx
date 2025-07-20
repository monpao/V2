import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  FileText, 
  Upload, 
  Download, 
  AlertTriangle,
  CheckCircle,
  Eye,
  Settings
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'

const StatementsPage = () => {
  const { user, API_BASE_URL } = useAuth()
  const [uploadedFile, setUploadedFile] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [results, setResults] = useState(null)
  const [selectedStandard, setSelectedStandard] = useState('SYSCOHADA')

  const standards = [
    { value: 'IFRS', label: 'IFRS - Normes Internationales' },
    { value: 'SYSCOHADA', label: 'SYSCOHADA Révisé' },
    { value: 'SYCEBNL', label: 'SYCEBNL' }
  ]

  const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      setUploadedFile(file)
      setResults(null)
    }
  }

  const processFinancialStatements = async () => {
    if (!uploadedFile) return

    setProcessing(true)
    
    try {
      const formData = new FormData()
      formData.append('balance_file', uploadedFile)
      formData.append('standard', selectedStandard)

      const response = await fetch(`${API_BASE_URL}/financial/statements/generate`, {
        method: 'POST',
        credentials: 'include',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        setResults(data)
      } else {
        console.error('Erreur lors du traitement')
      }
    } catch (error) {
      console.error('Erreur:', error)
    } finally {
      setProcessing(false)
    }
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
            États Financiers
          </h1>
          <p className="text-gray-600">
            Générez des états financiers conformes aux normes comptables à partir de votre balance
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Zone d'upload et configuration */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upload de fichier */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Upload className="h-5 w-5" />
                    <span>Téléverser la balance comptable</span>
                  </CardTitle>
                  <CardDescription>
                    Formats acceptés: PDF, Excel (.xlsx, .xls)
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                    <input
                      type="file"
                      accept=".pdf,.xlsx,.xls"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-lg font-medium text-gray-900 mb-2">
                        Cliquez pour sélectionner un fichier
                      </p>
                      <p className="text-sm text-gray-600">
                        ou glissez-déposez votre balance comptable ici
                      </p>
                    </label>
                  </div>
                  
                  {uploadedFile && (
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <div>
                          <p className="font-medium text-gray-900">{uploadedFile.name}</p>
                          <p className="text-sm text-gray-600">
                            {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Configuration */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Settings className="h-5 w-5" />
                    <span>Configuration</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Norme comptable
                      </label>
                      <select
                        value={selectedStandard}
                        onChange={(e) => setSelectedStandard(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        {standards.map((standard) => (
                          <option key={standard.value} value={standard.value}>
                            {standard.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="detect-anomalies"
                        defaultChecked
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="detect-anomalies" className="text-sm text-gray-700">
                        Détecter les anomalies automatiquement
                      </label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="generate-notes"
                        defaultChecked
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="generate-notes" className="text-sm text-gray-700">
                        Générer les notes annexes
                      </label>
                    </div>
                  </div>

                  <div className="mt-6">
                    <Button
                      onClick={processFinancialStatements}
                      disabled={!uploadedFile || processing}
                      className="w-full"
                    >
                      {processing ? (
                        <>
                          <LoadingSpinner size="sm" className="mr-2" />
                          Traitement en cours...
                        </>
                      ) : (
                        <>
                          <FileText className="mr-2 h-4 w-4" />
                          Générer les états financiers
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Informations et aide */}
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Fonctionnalités</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm">Bilan comptable</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm">Compte de résultat</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm">Tableau de flux de trésorerie</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm">Notes annexes</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm">Détection d'anomalies</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm">Analyses IA</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Normes supportées</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium text-gray-900">IFRS</h4>
                      <p className="text-sm text-gray-600">
                        Normes internationales d'information financière
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">SYSCOHADA Révisé</h4>
                      <p className="text-sm text-gray-600">
                        Système comptable OHADA révisé
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">SYCEBNL</h4>
                      <p className="text-sm text-gray-600">
                        Système comptable des entreprises BCEAO
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>

        {/* Résultats */}
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span>États financiers générés</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  <Button variant="outline" className="flex items-center justify-center space-x-2">
                    <Eye className="h-4 w-4" />
                    <span>Prévisualiser</span>
                  </Button>
                  <Button className="flex items-center justify-center space-x-2">
                    <Download className="h-4 w-4" />
                    <span>Télécharger PDF</span>
                  </Button>
                  <Button variant="outline" className="flex items-center justify-center space-x-2">
                    <Download className="h-4 w-4" />
                    <span>Télécharger Excel</span>
                  </Button>
                  <Button variant="outline" className="flex items-center justify-center space-x-2">
                    <AlertTriangle className="h-4 w-4" />
                    <span>Rapport d'anomalies</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default StatementsPage

