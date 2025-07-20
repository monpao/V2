from flask import Blueprint, request, jsonify, session, redirect
from src.models.user import db, User, AccountStatus
from datetime import datetime, timedelta
import logging

payment_bp = Blueprint('payment', __name__)

# Configuration des liens de paiement Fedapay
FEDAPAY_LINKS = {
    'monthly': 'https://me.fedapay.com/fincashmonthly',
    'annual': 'https://me.fedapay.com/fincashannually'
}

SUBSCRIPTION_PRICES = {
    'monthly': 30000,  # 30,000 FCFA
    'annual': 200000   # 200,000 FCFA
}

@payment_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """Récupère les plans d'abonnement disponibles"""
    plans = [
        {
            'id': 'demo',
            'name': 'Essai Gratuit',
            'price': 0,
            'currency': 'FCFA',
            'duration': 'Permanent',
            'features': [
                '3 exports gratuits',
                'Tous les modèles financiers',
                'Analyses IA basiques',
                'Support par email'
            ],
            'limitations': [
                'Limité à 3 exports',
                'Pas d\'historique étendu',
                'Support standard'
            ],
            'popular': False,
            'payment_link': None
        },
        {
            'id': 'monthly',
            'name': 'Abonnement Mensuel',
            'price': 30000,
            'currency': 'FCFA',
            'duration': 'Par mois',
            'features': [
                'Exports illimités',
                'Tous les modèles financiers',
                'Analyses IA avancées',
                'Génération d\'états financiers',
                'Support prioritaire',
                'Historique complet',
                'Multi-devises'
            ],
            'limitations': [],
            'popular': True,
            'payment_link': FEDAPAY_LINKS['monthly']
        },
        {
            'id': 'annual',
            'name': 'Abonnement Annuel',
            'price': 200000,
            'currency': 'FCFA',
            'duration': 'Par an',
            'savings': 160000,  # Économie par rapport au mensuel
            'features': [
                'Exports illimités',
                'Tous les modèles financiers',
                'Analyses IA avancées',
                'Génération d\'états financiers',
                'Support prioritaire VIP',
                'Historique complet',
                'Multi-devises',
                'Formation personnalisée',
                'API access'
            ],
            'limitations': [],
            'popular': False,
            'payment_link': FEDAPAY_LINKS['annual']
        }
    ]
    
    return jsonify({'plans': plans})

@payment_bp.route('/user/subscription', methods=['GET'])
def get_user_subscription():
    """Récupère les informations d'abonnement de l'utilisateur"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    subscription_info = {
        'current_plan': user.account_status.value,
        'free_exports_used': user.free_exports_used,
        'free_exports_remaining': max(0, 3 - user.free_exports_used) if user.account_status.value == 'demo' else 'illimité',
        'subscription_start': user.subscription_start.isoformat() if user.subscription_start else None,
        'subscription_end': user.subscription_end.isoformat() if user.subscription_end else None,
        'is_active': user.is_subscription_active(),
        'days_remaining': user.get_subscription_days_remaining(),
        'can_export': user.can_export()
    }
    
    return jsonify(subscription_info)

@payment_bp.route('/initiate/<plan_type>', methods=['POST'])
def initiate_payment(plan_type):
    """Initie un paiement pour un plan d'abonnement"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    if plan_type not in ['monthly', 'annual']:
        return jsonify({'error': 'Plan d\'abonnement invalide'}), 400
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Vérifier si l'utilisateur a déjà un abonnement actif
    if user.is_subscription_active() and user.account_status.value != 'demo':
        return jsonify({
            'error': 'Abonnement déjà actif',
            'message': 'Vous avez déjà un abonnement actif. Contactez le support pour modifier votre plan.'
        }), 400
    
    payment_data = {
        'plan_type': plan_type,
        'price': SUBSCRIPTION_PRICES[plan_type],
        'currency': 'FCFA',
        'payment_link': FEDAPAY_LINKS[plan_type],
        'user_id': user.id,
        'user_email': user.email,
        'return_url': request.host_url + 'payment/success',
        'cancel_url': request.host_url + 'payment/cancel'
    }
    
    # Log de la tentative de paiement
    logging.info(f"Initiation de paiement pour l'utilisateur {user.username} - Plan: {plan_type}")
    
    return jsonify({
        'success': True,
        'payment_data': payment_data,
        'message': 'Redirection vers la page de paiement'
    })

@payment_bp.route('/success', methods=['GET', 'POST'])
def payment_success():
    """Gère le retour de paiement réussi"""
    # Dans un vrai système, on vérifierait la signature et les données de Fedapay
    user_id = request.args.get('user_id') or request.form.get('user_id')
    plan_type = request.args.get('plan_type') or request.form.get('plan_type')
    transaction_id = request.args.get('transaction_id') or request.form.get('transaction_id')
    
    if not user_id or not plan_type:
        return jsonify({'error': 'Données de paiement manquantes'}), 400
    
    try:
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Activer l'abonnement
        success = user.activate_subscription(plan_type)
        
        if success:
            # Log du paiement réussi
            logging.info(f"Paiement réussi pour l'utilisateur {user.username} - Plan: {plan_type} - Transaction: {transaction_id}")
            
            return jsonify({
                'success': True,
                'message': 'Abonnement activé avec succès',
                'subscription': {
                    'plan': plan_type,
                    'start_date': user.subscription_start.isoformat(),
                    'end_date': user.subscription_end.isoformat(),
                    'status': user.account_status.value
                }
            })
        else:
            return jsonify({'error': 'Erreur lors de l\'activation de l\'abonnement'}), 500
            
    except Exception as e:
        logging.error(f"Erreur lors du traitement du paiement réussi: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@payment_bp.route('/cancel', methods=['GET'])
def payment_cancel():
    """Gère l'annulation de paiement"""
    user_id = request.args.get('user_id')
    plan_type = request.args.get('plan_type')
    
    # Log de l'annulation
    if user_id:
        user = User.query.get(int(user_id))
        if user:
            logging.info(f"Paiement annulé pour l'utilisateur {user.username} - Plan: {plan_type}")
    
    return jsonify({
        'success': False,
        'message': 'Paiement annulé',
        'redirect_url': '/dashboard'
    })

@payment_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """Webhook pour recevoir les notifications de paiement de Fedapay"""
    try:
        # Vérifier la signature du webhook (à implémenter selon la documentation Fedapay)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        event_type = data.get('event')
        transaction_data = data.get('data', {})
        
        if event_type == 'transaction.approved':
            # Traitement du paiement approuvé
            user_email = transaction_data.get('customer', {}).get('email')
            amount = transaction_data.get('amount')
            transaction_id = transaction_data.get('id')
            
            if user_email:
                user = User.query.filter_by(email=user_email).first()
                if user:
                    # Déterminer le type de plan basé sur le montant
                    plan_type = 'monthly' if amount == SUBSCRIPTION_PRICES['monthly'] else 'annual'
                    
                    # Activer l'abonnement
                    success = user.activate_subscription(plan_type)
                    
                    if success:
                        logging.info(f"Abonnement activé via webhook pour {user.username} - Transaction: {transaction_id}")
                        return jsonify({'status': 'success'})
        
        elif event_type == 'transaction.declined':
            # Traitement du paiement refusé
            logging.warning(f"Paiement refusé - Transaction: {transaction_data.get('id')}")
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        logging.error(f"Erreur lors du traitement du webhook: {str(e)}")
        return jsonify({'error': 'Erreur interne'}), 500

@payment_bp.route('/upgrade-info', methods=['GET'])
def get_upgrade_info():
    """Récupère les informations pour encourager la mise à niveau"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    upgrade_info = {
        'current_plan': user.account_status.value,
        'exports_used': user.free_exports_used,
        'exports_remaining': max(0, 3 - user.free_exports_used) if user.account_status.value == 'demo' else 'illimité',
        'should_upgrade': not user.can_export() and user.account_status.value == 'demo',
        'benefits': [
            'Exports illimités de modèles financiers',
            'Analyses IA avancées et personnalisées',
            'Génération d\'états financiers professionnels',
            'Support prioritaire et formation',
            'Historique complet de vos analyses',
            'Accès à tous les modèles financiers',
            'Multi-devises et personnalisation'
        ],
        'monthly_savings': 'Flexibilité maximale',
        'annual_savings': f'Économisez {160000:,} FCFA par an',
        'contact': {
            'email': 'fincashinfos@gmail.com',
            'phone': '+229 01 43 20 21 21'
        }
    }
    
    return jsonify(upgrade_info)

@payment_bp.route('/admin/subscriptions', methods=['GET'])
def admin_get_subscriptions():
    """Récupère toutes les informations d'abonnement pour l'admin"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = User.query.get(session['user_id'])
    if not user or user.role.value != 'ADMIN':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    users = User.query.all()
    subscriptions = []
    
    for u in users:
        subscription = {
            'user_id': u.id,
            'username': u.username,
            'email': u.email,
            'account_status': u.account_status.value,
            'subscription_start': u.subscription_start.isoformat() if u.subscription_start else None,
            'subscription_end': u.subscription_end.isoformat() if u.subscription_end else None,
            'is_active': u.is_subscription_active(),
            'days_remaining': u.get_subscription_days_remaining(),
            'free_exports_used': u.free_exports_used,
            'created_at': u.created_at.isoformat(),
            'last_login': u.last_login.isoformat() if u.last_login else None
        }
        subscriptions.append(subscription)
    
    # Statistiques
    total_users = len(users)
    demo_users = len([u for u in users if u.account_status.value == 'demo'])
    monthly_users = len([u for u in users if u.account_status.value == 'monthly'])
    annual_users = len([u for u in users if u.account_status.value == 'annual'])
    active_subscriptions = monthly_users + annual_users
    
    total_revenue = (monthly_users * SUBSCRIPTION_PRICES['monthly']) + (annual_users * SUBSCRIPTION_PRICES['annual'])
    
    stats = {
        'total_users': total_users,
        'demo_users': demo_users,
        'monthly_users': monthly_users,
        'annual_users': annual_users,
        'active_subscriptions': active_subscriptions,
        'total_revenue': total_revenue,
        'conversion_rate': (active_subscriptions / total_users * 100) if total_users > 0 else 0
    }
    
    return jsonify({
        'subscriptions': subscriptions,
        'stats': stats
    })

