import React, { useState, useEffect } from 'react';
import { Check, X, Star, Zap, Shield, Headphones, TrendingUp, ExternalLink } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const PricingSection = ({ showTitle = true, compact = false }) => {
  const { user, API_BASE_URL } = useAuth();
  const [plans, setPlans] = useState([]);
  const [userSubscription, setUserSubscription] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlans();
    if (user) {
      fetchUserSubscription();
    }
  }, [user]);

  const fetchPlans = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/payment/plans`);
      if (response.ok) {
        const data = await response.json();
        setPlans(data.plans);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserSubscription = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/payment/user/subscription`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setUserSubscription(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement de l\'abonnement:', error);
    }
  };

  const handleSubscribe = async (planId) => {
    if (!user) {
      // Rediriger vers la page de connexion
      window.location.href = '/login';
      return;
    }

    if (planId === 'demo') {
      // Déjà sur le plan gratuit
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/payment/initiate/${planId}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.payment_data.payment_link) {
          // Rediriger vers Fedapay
          window.open(data.payment_data.payment_link, '_blank');
        }
      } else {
        const errorData = await response.json();
        alert(errorData.message || 'Erreur lors de l\'initiation du paiement');
      }
    } catch (error) {
      console.error('Erreur lors de l\'initiation du paiement:', error);
      alert('Erreur lors de l\'initiation du paiement');
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'XOF',
      minimumFractionDigits: 0
    }).format(price);
  };

  const getPlanIcon = (planId) => {
    switch (planId) {
      case 'demo':
        return <Shield className="h-6 w-6" />;
      case 'monthly':
        return <Zap className="h-6 w-6" />;
      case 'annual':
        return <Star className="h-6 w-6" />;
      default:
        return <TrendingUp className="h-6 w-6" />;
    }
  };

  const getButtonText = (plan) => {
    if (!user) {
      return plan.id === 'demo' ? 'Commencer gratuitement' : 'S\'abonner';
    }

    if (userSubscription?.current_plan === plan.id) {
      return 'Plan actuel';
    }

    if (plan.id === 'demo') {
      return 'Plan gratuit';
    }

    return 'Choisir ce plan';
  };

  const isCurrentPlan = (planId) => {
    return userSubscription?.current_plan === planId;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className={`${compact ? 'py-8' : 'py-16'} bg-gray-50`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {showTitle && (
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Choisissez votre plan
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Des solutions adaptées à tous les besoins, de l'essai gratuit aux fonctionnalités professionnelles avancées
            </p>
          </div>
        )}

        <div className={`grid ${compact ? 'grid-cols-1 md:grid-cols-3' : 'grid-cols-1 md:grid-cols-3'} gap-8 max-w-6xl mx-auto`}>
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`relative bg-white rounded-2xl shadow-lg overflow-hidden ${
                plan.popular ? 'ring-2 ring-blue-500 scale-105' : ''
              } ${isCurrentPlan(plan.id) ? 'ring-2 ring-green-500' : ''}`}
            >
              {plan.popular && (
                <div className="absolute top-0 left-0 right-0 bg-blue-500 text-white text-center py-2 text-sm font-medium">
                  Le plus populaire
                </div>
              )}

              {isCurrentPlan(plan.id) && (
                <div className="absolute top-0 left-0 right-0 bg-green-500 text-white text-center py-2 text-sm font-medium">
                  Votre plan actuel
                </div>
              )}

              <div className={`p-8 ${plan.popular || isCurrentPlan(plan.id) ? 'pt-12' : ''}`}>
                {/* En-tête du plan */}
                <div className="text-center mb-8">
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full mb-4 ${
                    plan.id === 'demo' ? 'bg-gray-100 text-gray-600' :
                    plan.id === 'monthly' ? 'bg-blue-100 text-blue-600' :
                    'bg-purple-100 text-purple-600'
                  }`}>
                    {getPlanIcon(plan.id)}
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <div className="mb-4">
                    <span className="text-4xl font-bold text-gray-900">
                      {plan.price === 0 ? 'Gratuit' : formatPrice(plan.price)}
                    </span>
                    {plan.price > 0 && (
                      <span className="text-gray-600 ml-2">/ {plan.duration.toLowerCase()}</span>
                    )}
                  </div>
                  {plan.savings && (
                    <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                      Économisez {formatPrice(plan.savings)}
                    </div>
                  )}
                </div>

                {/* Fonctionnalités */}
                <div className="mb-8">
                  <h4 className="font-semibold text-gray-900 mb-4">Fonctionnalités incluses :</h4>
                  <ul className="space-y-3">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <Check className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Limitations */}
                {plan.limitations && plan.limitations.length > 0 && (
                  <div className="mb-8">
                    <h4 className="font-semibold text-gray-900 mb-4">Limitations :</h4>
                    <ul className="space-y-3">
                      {plan.limitations.map((limitation, index) => (
                        <li key={index} className="flex items-start">
                          <X className="h-5 w-5 text-red-500 mr-3 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-600">{limitation}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Bouton d'action */}
                <button
                  onClick={() => handleSubscribe(plan.id)}
                  disabled={isCurrentPlan(plan.id) || (plan.id === 'demo' && user)}
                  className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${
                    isCurrentPlan(plan.id)
                      ? 'bg-green-100 text-green-800 cursor-not-allowed'
                      : plan.popular
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-900 text-white hover:bg-gray-800'
                  } ${(plan.id === 'demo' && user) ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {getButtonText(plan)}
                  {plan.payment_link && !isCurrentPlan(plan.id) && (
                    <ExternalLink className="inline-block ml-2 h-4 w-4" />
                  )}
                </button>

                {/* Informations supplémentaires */}
                {plan.id !== 'demo' && (
                  <div className="mt-4 text-center">
                    <p className="text-sm text-gray-600">
                      Paiement sécurisé via Fedapay
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Informations de contact */}
        <div className="mt-12 text-center">
          <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Besoin d'aide pour choisir ?
            </h3>
            <p className="text-gray-600 mb-4">
              Notre équipe est là pour vous accompagner dans votre choix et répondre à toutes vos questions.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-6">
              <div className="flex items-center">
                <Headphones className="h-5 w-5 text-blue-600 mr-2" />
                <span className="text-gray-700">+229 01 43 20 21 21</span>
              </div>
              <div className="flex items-center">
                <svg className="h-5 w-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                </svg>
                <span className="text-gray-700">fincashinfos@gmail.com</span>
              </div>
            </div>
          </div>
        </div>

        {/* Garanties */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <Shield className="h-6 w-6 text-blue-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Sécurité garantie</h4>
            <p className="text-gray-600 text-sm">Vos données sont chiffrées et protégées selon les standards internationaux</p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <Headphones className="h-6 w-6 text-green-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Support dédié</h4>
            <p className="text-gray-600 text-sm">Une équipe d'experts à votre disposition pour vous accompagner</p>
          </div>
          <div className="text-center">
            <div className="bg-purple-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Évolution continue</h4>
            <p className="text-gray-600 text-sm">Nouvelles fonctionnalités et améliorations régulières incluses</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingSection;

