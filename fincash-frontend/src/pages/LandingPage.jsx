import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  TrendingUp, 
  Shield, 
  Zap, 
  Users, 
  Award,
  ChevronRight,
  Mail,
  Phone,
  MapPin,
  CheckCircle,
  ArrowRight,
  Star
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import PricingSection from '../components/PricingSection'
import { Textarea } from '@/components/ui/textarea'

const LandingPage = () => {
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    company: '',
    message: ''
  })

  const handleContactSubmit = (e) => {
    e.preventDefault()
    // Ici, vous pouvez ajouter la logique d'envoi du formulaire
    console.log('Formulaire de contact soumis:', contactForm)
    alert('Merci pour votre message ! Nous vous recontacterons bientôt.')
    setContactForm({ name: '', email: '', company: '', message: '' })
  }

  const features = [
    {
      icon: BarChart3,
      title: 'Modèles Financiers Avancés',
      description: 'DCF, LBO, évaluation d\'obligations, Black-Scholes et plus de 10 modèles professionnels'
    },
    {
      icon: TrendingUp,
      title: 'Analyses IA Intégrées',
      description: 'Recommandations intelligentes et insights basés sur l\'intelligence artificielle'
    },
    {
      icon: Shield,
      title: 'Conformité Réglementaire',
      description: 'Support des normes IFRS, SYSCOHADA révisé et SYCEBNL'
    },
    {
      icon: Zap,
      title: 'Exports Professionnels',
      description: 'Génération de rapports PDF et Excel de qualité supérieure avec graphiques'
    }
  ]

  const pricingPlans = [
    {
      name: 'Démo',
      price: 'Gratuit',
      period: '',
      description: '3 exportations gratuites pour tester',
      features: [
        'Accès à tous les modèles financiers',
        '3 exportations PDF/Excel',
        'Analyses IA basiques',
        'Support par email'
      ],
      cta: 'Commencer gratuitement',
      popular: false
    },
    {
      name: 'Mensuel',
      price: '30 000',
      period: 'FCFA/mois',
      description: 'Pour les professionnels actifs',
      features: [
        'Exportations illimitées',
        'Tous les modèles financiers',
        'Analyses IA avancées',
        'États financiers automatisés',
        'Support prioritaire',
        'Multi-devises'
      ],
      cta: 'Choisir Mensuel',
      popular: true,
      paymentLink: 'https://me.fedapay.com/fincashmonthly'
    },
    {
      name: 'Annuel',
      price: '200 000',
      period: 'FCFA/an',
      description: 'Économisez 44% avec l\'abonnement annuel',
      features: [
        'Tout du plan mensuel',
        'Économies importantes',
        'Rapports personnalisés',
        'Formation incluse',
        'Support dédié',
        'Intégrations API'
      ],
      cta: 'Choisir Annuel',
      popular: false,
      paymentLink: 'https://me.fedapay.com/fincashannually'
    }
  ]

  const testimonials = [
    {
      name: 'Marie Kouassi',
      role: 'Directrice Financière',
      company: 'Groupe NSIA',
      content: 'Fincash a révolutionné notre approche de la modélisation financière. Les analyses IA nous font gagner un temps précieux.',
      rating: 5
    },
    {
      name: 'Jean-Baptiste Tano',
      role: 'Consultant en Finance',
      company: 'Cabinet Expertise+',
      content: 'La qualité des exports et la conformité aux normes SYSCOHADA font de Fincash un outil indispensable.',
      rating: 5
    },
    {
      name: 'Fatou Diallo',
      role: 'Analyste Financier',
      company: 'Banque Atlantique',
      content: 'Interface intuitive et modèles sophistiqués. Parfait pour nos analyses d\'investissement.',
      rating: 5
    }
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-2xl font-bold text-blue-600"
            >
              Fincash
            </motion.div>
            
            <nav className="hidden md:flex space-x-8">
              <a href="#features" className="text-gray-700 hover:text-blue-600 transition-colors">
                Fonctionnalités
              </a>
              <a href="#pricing" className="text-gray-700 hover:text-blue-600 transition-colors">
                Tarifs
              </a>
              <a href="#contact" className="text-gray-700 hover:text-blue-600 transition-colors">
                Contact
              </a>
            </nav>

            <div className="flex items-center space-x-4">
              <Link to="/login">
                <Button variant="ghost">Connexion</Button>
              </Link>
              <Link to="/register">
                <Button>Inscription</Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-4xl md:text-6xl font-bold text-gray-900 mb-6"
            >
              Modélisation Financière
              <span className="text-blue-600 block">Professionnelle</span>
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto"
            >
              Plateforme complète de modélisation financière avec IA intégrée, 
              conforme aux normes IFRS, SYSCOHADA et SYCEBNL. 
              Créez des analyses professionnelles en quelques clics.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link to="/register">
                <Button size="lg" className="text-lg px-8 py-3">
                  Essayer gratuitement
                  <ArrowRight className="ml-2" size={20} />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="text-lg px-8 py-3">
                Voir la démo
              </Button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="mt-12 flex justify-center items-center space-x-8 text-sm text-gray-500"
            >
              <div className="flex items-center">
                <CheckCircle className="text-green-500 mr-2" size={16} />
                3 exports gratuits
              </div>
              <div className="flex items-center">
                <CheckCircle className="text-green-500 mr-2" size={16} />
                Aucune carte requise
              </div>
              <div className="flex items-center">
                <CheckCircle className="text-green-500 mr-2" size={16} />
                Configuration en 2 minutes
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Fonctionnalités Avancées
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Tous les outils dont vous avez besoin pour une modélisation financière professionnelle
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="text-center p-6 rounded-lg hover:shadow-lg transition-shadow"
              >
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="text-blue-600" size={32} />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Tarifs Transparents
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Choisissez le plan qui correspond à vos besoins
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={`relative bg-white rounded-lg shadow-lg p-8 ${
                  plan.popular ? 'ring-2 ring-blue-600 scale-105' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Plus populaire
                    </span>
                  </div>
                )}

                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    {plan.name}
                  </h3>
                  <div className="mb-2">
                    <span className="text-4xl font-bold text-gray-900">
                      {plan.price}
                    </span>
                    {plan.period && (
                      <span className="text-gray-600 ml-1">
                        {plan.period}
                      </span>
                    )}
                  </div>
                  <p className="text-gray-600">
                    {plan.description}
                  </p>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center">
                      <CheckCircle className="text-green-500 mr-3 flex-shrink-0" size={16} />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                {plan.paymentLink ? (
                  <a href={plan.paymentLink} target="_blank" rel="noopener noreferrer">
                    <Button 
                      className="w-full" 
                      variant={plan.popular ? 'default' : 'outline'}
                    >
                      {plan.cta}
                    </Button>
                  </a>
                ) : (
                  <Link to="/register">
                    <Button 
                      className="w-full" 
                      variant={plan.popular ? 'default' : 'outline'}
                    >
                      {plan.cta}
                    </Button>
                  </Link>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Ce que disent nos clients
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Rejoignez des centaines de professionnels qui font confiance à Fincash
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-gray-50 rounded-lg p-6"
              >
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="text-yellow-400 fill-current" size={16} />
                  ))}
                </div>
                <p className="text-gray-700 mb-4 italic">
                  "{testimonial.content}"
                </p>
                <div>
                  <div className="font-semibold text-gray-900">
                    {testimonial.name}
                  </div>
                  <div className="text-sm text-gray-600">
                    {testimonial.role}, {testimonial.company}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12">
            {/* Informations de contact */}
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                Contactez-nous
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                Notre équipe est là pour répondre à vos questions et vous accompagner 
                dans votre transformation financière digitale.
              </p>

              <div className="space-y-6">
                <div className="flex items-center">
                  <Mail className="text-blue-600 mr-4" size={24} />
                  <div>
                    <div className="font-semibold text-gray-900">Email</div>
                    <div className="text-gray-600">fincashinfos@gmail.com</div>
                  </div>
                </div>

                <div className="flex items-center">
                  <Phone className="text-blue-600 mr-4" size={24} />
                  <div>
                    <div className="font-semibold text-gray-900">Téléphone</div>
                    <div className="text-gray-600">+229 01 43 20 21 21</div>
                  </div>
                </div>

                <div className="flex items-center">
                  <MapPin className="text-blue-600 mr-4" size={24} />
                  <div>
                    <div className="font-semibold text-gray-900">Localisation</div>
                    <div className="text-gray-600">Afrique de l'Ouest</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Formulaire de contact */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <form onSubmit={handleContactSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nom complet *
                  </label>
                  <Input
                    type="text"
                    required
                    value={contactForm.name}
                    onChange={(e) => setContactForm({...contactForm, name: e.target.value})}
                    placeholder="Votre nom complet"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <Input
                    type="email"
                    required
                    value={contactForm.email}
                    onChange={(e) => setContactForm({...contactForm, email: e.target.value})}
                    placeholder="votre@email.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Entreprise
                  </label>
                  <Input
                    type="text"
                    value={contactForm.company}
                    onChange={(e) => setContactForm({...contactForm, company: e.target.value})}
                    placeholder="Nom de votre entreprise"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message *
                  </label>
                  <Textarea
                    required
                    rows={4}
                    value={contactForm.message}
                    onChange={(e) => setContactForm({...contactForm, message: e.target.value})}
                    placeholder="Décrivez votre projet ou vos besoins..."
                  />
                </div>

                <Button type="submit" className="w-full">
                  Envoyer le message
                  <ChevronRight className="ml-2" size={16} />
                </Button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="text-2xl font-bold text-blue-400 mb-4">
                Fincash
              </div>
              <p className="text-gray-400">
                Plateforme de modélisation financière professionnelle 
                pour l'Afrique de l'Ouest.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Produit</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#features" className="hover:text-white transition-colors">Fonctionnalités</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Tarifs</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#contact" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Centre d'aide</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Formation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Communauté</a></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Légal</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Conditions d'utilisation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Politique de confidentialité</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Mentions légales</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Fincash. Tous droits réservés.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage

