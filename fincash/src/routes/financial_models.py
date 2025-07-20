from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, FinancialModel, Task
from src.financial_engine import FinancialEngine
from src.ai_advisor import AIFinancialAdvisor
from datetime import datetime
import json

financial_models_bp = Blueprint('financial_models', __name__)

def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentification requise'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Instances des moteurs
financial_engine = FinancialEngine()
ai_advisor = AIFinancialAdvisor()

# Liste des modèles financiers disponibles
AVAILABLE_MODELS = {
    'dcf': {
        'name': 'Analyse des flux de trésorerie actualisés (DCF)',
        'description': 'Évaluation d\'entreprise basée sur les flux de trésorerie futurs actualisés',
        'parameters': ['revenus_initiaux', 'taux_croissance', 'taux_actualisation', 'duree_projection', 'croissance_terminale', 'marge_ebitda', 'taux_impot']
    },
    'investment_budgeting': {
        'name': 'Budget d\'investissement en capital',
        'description': 'Analyse de la rentabilité des investissements en capital',
        'parameters': ['investissement_initial', 'flux_annuels', 'taux_actualisation', 'duree_vie']
    },
    'financial_planning': {
        'name': 'Planification financière',
        'description': 'Modèle de planification financière intégrée',
        'parameters': ['revenus_prevus', 'charges_prevues', 'investissements', 'financement']
    },
    'loan_amortization': {
        'name': 'Amortissement de prêt',
        'description': 'Calcul des échéances et du plan d\'amortissement',
        'parameters': ['montant_pret', 'taux_interet', 'duree_mois', 'type_amortissement']
    },
    'bond_pricing': {
        'name': 'Évaluation d\'obligations',
        'description': 'Calcul du prix et du rendement des obligations',
        'parameters': ['valeur_nominale', 'taux_coupon', 'taux_marche', 'echeance', 'frequence_paiement']
    },
    'black_scholes': {
        'name': 'Modèle Black-Scholes',
        'description': 'Évaluation d\'options européennes',
        'parameters': ['prix_actif', 'prix_exercice', 'taux_sans_risque', 'volatilite', 'temps_echeance', 'type_option']
    },
    'financial_ratios': {
        'name': 'Analyse des ratios financiers',
        'description': 'Calcul et analyse des ratios de performance financière',
        'parameters': ['actif_total', 'actif_circulant', 'tresorerie', 'stocks', 'creances', 'passif_total', 'passif_circulant', 'dettes_long_terme', 'chiffre_affaires', 'benefice_brut', 'benefice_exploitation', 'benefice_net', 'charges_financieres']
    },
    'real_estate_valuation': {
        'name': 'Évaluation immobilière commerciale',
        'description': 'Analyse de faisabilité et évaluation immobilière',
        'parameters': ['revenus_locatifs', 'charges_exploitation', 'taux_capitalisation', 'taux_actualisation']
    },
    'lbo_analysis': {
        'name': 'Analyse LBO (Leveraged Buyout)',
        'description': 'Modèle d\'acquisition avec effet de levier',
        'parameters': ['prix_acquisition', 'dette_initiale', 'ebitda', 'taux_croissance', 'multiple_sortie']
    },
    'merger_analysis': {
        'name': 'Analyse de fusion-acquisition',
        'description': 'Évaluation des synergies et impact financier des M&A',
        'parameters': ['valeur_cible', 'synergies_revenus', 'synergies_couts', 'prime_acquisition']
    }
}

@financial_models_bp.route('/models', methods=['GET'])
@require_auth
def get_available_models():
    """Retourne la liste des modèles financiers disponibles"""
    return jsonify({'models': AVAILABLE_MODELS}), 200

@financial_models_bp.route('/models/<model_type>/calculate', methods=['POST'])
@require_auth
def calculate_model(model_type):
    """Exécute un modèle financier avec les paramètres fournis"""
    try:
        if model_type not in AVAILABLE_MODELS:
            return jsonify({'error': 'Modèle financier non trouvé'}), 404
        
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Paramètres requis'}), 400
        
        # Créer une tâche pour le calcul
        task = Task(
            task_type=f'financial_model_{model_type}',
            status='processing',
            input_data=data,
            user_id=user_id
        )
        db.session.add(task)
        db.session.commit()
        
        # Calculer le modèle (simulation pour l'instant)
        results = calculate_financial_model(model_type, data)
        
        # Ajouter l'analyse IA si disponible
        if 'error' not in results:
            try:
                if model_type == 'dcf':
                    ai_analysis = ai_advisor.generate_dcf_analysis(results, data)
                    results['analyse_ia'] = ai_analysis
                elif model_type == 'investment_budgeting':
                    ai_analysis = ai_advisor.generate_investment_analysis(results, data)
                    results['analyse_ia'] = ai_analysis
                elif model_type == 'financial_ratios':
                    ai_analysis = ai_advisor.generate_financial_health_report(results, data)
                    results['analyse_ia'] = ai_analysis
                else:
                    # Analyse générale pour les autres modèles
                    ai_analysis = ai_advisor.generate_market_insights(results, data)
                    results['analyse_ia'] = ai_analysis
            except Exception as e:
                # Si l'IA échoue, continuer sans l'analyse IA
                results['analyse_ia'] = {'error': f'Analyse IA indisponible: {str(e)}'}
        
        # Sauvegarder le modèle financier
        financial_model = FinancialModel(
            name=data.get('name', f'{AVAILABLE_MODELS[model_type]["name"]} - {datetime.now().strftime("%Y-%m-%d %H:%M")}'),
            model_type=model_type,
            description=AVAILABLE_MODELS[model_type]['description'],
            parameters=data,
            results=results,
            user_id=user_id
        )
        db.session.add(financial_model)
        
        # Mettre à jour la tâche
        task.status = 'completed'
        task.output_data = results
        task.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Calcul terminé avec succès',
            'model': financial_model.to_dict(),
            'task_id': task.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors du calcul: {str(e)}'}), 500

@financial_models_bp.route('/models/user', methods=['GET'])
@require_auth
def get_user_models():
    """Retourne les modèles financiers de l'utilisateur"""
    user_id = session['user_id']
    models = FinancialModel.query.filter_by(user_id=user_id).order_by(FinancialModel.created_at.desc()).all()
    
    return jsonify({
        'models': [model.to_dict() for model in models]
    }), 200

@financial_models_bp.route('/models/<int:model_id>', methods=['GET'])
@require_auth
def get_model(model_id):
    """Retourne un modèle financier spécifique"""
    user_id = session['user_id']
    model = FinancialModel.query.filter_by(id=model_id, user_id=user_id).first()
    
    if not model:
        return jsonify({'error': 'Modèle non trouvé'}), 404
    
    return jsonify({'model': model.to_dict()}), 200

@financial_models_bp.route('/models/<int:model_id>/export', methods=['POST'])
@require_auth
def export_model(model_id):
    """Exporte un modèle financier en PDF ou Excel"""
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        model = FinancialModel.query.filter_by(id=model_id, user_id=user_id).first()
        
        if not model:
            return jsonify({'error': 'Modèle non trouvé'}), 404
        
        if not user.can_export():
            return jsonify({
                'error': 'Limite d\'exportation atteinte. Veuillez souscrire à un abonnement.',
                'upgrade_required': True
            }), 403
        
        data = request.get_json()
        export_format = data.get('format', 'pdf')  # pdf ou excel
        
        if export_format not in ['pdf', 'excel']:
            return jsonify({'error': 'Format d\'export non supporté'}), 400
        
        # Utiliser un export gratuit si en mode démo
        if user.account_status.value == 'demo':
            user.use_free_export()
        
        # Générer l'export (simulation pour l'instant)
        export_result = generate_export(model, export_format)
        
        return jsonify({
            'message': 'Export généré avec succès',
            'export_url': export_result['url'],
            'remaining_free_exports': 3 - user.free_exports_used if user.account_status.value == 'demo' else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500

def calculate_financial_model(model_type, parameters):
    """Calcule un modèle financier en utilisant le moteur financier avancé"""
    
    if model_type == 'dcf':
        return financial_engine.calculate_dcf(parameters)
    elif model_type == 'investment_budgeting':
        return financial_engine.calculate_investment_budgeting(parameters)
    elif model_type == 'loan_amortization':
        return financial_engine.calculate_loan_amortization(parameters)
    elif model_type == 'bond_pricing':
        return financial_engine.calculate_bond_pricing(parameters)
    elif model_type == 'black_scholes':
        return financial_engine.calculate_black_scholes(parameters)
    elif model_type == 'financial_ratios':
        return financial_engine.calculate_financial_ratios(parameters)
    elif model_type == 'financial_planning':
        return calculate_financial_planning(parameters)
    elif model_type == 'real_estate_valuation':
        return calculate_real_estate_valuation(parameters)
    elif model_type == 'lbo_analysis':
        return calculate_lbo_analysis(parameters)
    elif model_type == 'merger_analysis':
        return calculate_merger_analysis(parameters)
    else:
        return {'error': 'Modèle non implémenté'}

def calculate_dcf(params):
    """Calcul DCF simplifié"""
    revenus_initiaux = float(params.get('revenus_initiaux', 1000000))
    taux_croissance = float(params.get('taux_croissance', 0.05))
    taux_actualisation = float(params.get('taux_actualisation', 0.10))
    duree_projection = int(params.get('duree_projection', 5))
    
    flux_projetes = []
    valeur_actuelle_totale = 0
    
    for annee in range(1, duree_projection + 1):
        flux_annuel = revenus_initiaux * ((1 + taux_croissance) ** annee)
        valeur_actuelle = flux_annuel / ((1 + taux_actualisation) ** annee)
        flux_projetes.append({
            'annee': annee,
            'flux_brut': flux_annuel,
            'valeur_actuelle': valeur_actuelle
        })
        valeur_actuelle_totale += valeur_actuelle
    
    # Valeur terminale (simplifiée)
    flux_terminal = revenus_initiaux * ((1 + taux_croissance) ** (duree_projection + 1))
    valeur_terminale = (flux_terminal / (taux_actualisation - taux_croissance)) / ((1 + taux_actualisation) ** duree_projection)
    
    valeur_entreprise = valeur_actuelle_totale + valeur_terminale
    
    return {
        'flux_projetes': flux_projetes,
        'valeur_actuelle_flux': valeur_actuelle_totale,
        'valeur_terminale': valeur_terminale,
        'valeur_entreprise': valeur_entreprise,
        'parametres': params,
        'recommandations': [
            f"La valeur de l'entreprise est estimée à {valeur_entreprise:,.0f} FCFA",
            f"La valeur terminale représente {(valeur_terminale/valeur_entreprise)*100:.1f}% de la valeur totale",
            "Considérez la sensibilité aux hypothèses de croissance et de taux d'actualisation"
        ]
    }

def calculate_investment_budgeting(params):
    """Calcul budget d'investissement simplifié"""
    investissement_initial = float(params.get('investissement_initial', 1000000))
    flux_annuels = float(params.get('flux_annuels', 200000))
    taux_actualisation = float(params.get('taux_actualisation', 0.10))
    duree_vie = int(params.get('duree_vie', 5))
    
    van = -investissement_initial
    flux_actualises = []
    
    for annee in range(1, duree_vie + 1):
        flux_actualise = flux_annuels / ((1 + taux_actualisation) ** annee)
        flux_actualises.append({
            'annee': annee,
            'flux_brut': flux_annuels,
            'flux_actualise': flux_actualise
        })
        van += flux_actualise
    
    # Calcul du TRI (approximation)
    tir = taux_actualisation  # Simplification pour la démo
    
    # Délai de récupération
    delai_recuperation = investissement_initial / flux_annuels
    
    return {
        'investissement_initial': investissement_initial,
        'flux_actualises': flux_actualises,
        'van': van,
        'tir': tir,
        'delai_recuperation': delai_recuperation,
        'rentable': van > 0,
        'recommandations': [
            f"VAN: {van:,.0f} FCFA - {'Projet rentable' if van > 0 else 'Projet non rentable'}",
            f"Délai de récupération: {delai_recuperation:.1f} années",
            f"TIR estimé: {tir*100:.1f}%"
        ]
    }

def calculate_financial_planning(params):
    """Calcul planification financière simplifié"""
    # Implémentation simplifiée pour la démo
    return {
        'message': 'Modèle de planification financière calculé',
        'parametres': params,
        'recommandations': ['Planification financière en cours de développement']
    }

def calculate_loan_amortization(params):
    """Calcul amortissement de prêt"""
    montant_pret = float(params.get('montant_pret', 1000000))
    taux_interet = float(params.get('taux_interet', 0.05)) / 12  # Taux mensuel
    duree_mois = int(params.get('duree_mois', 60))
    
    # Calcul de la mensualité
    if taux_interet > 0:
        mensualite = montant_pret * (taux_interet * (1 + taux_interet)**duree_mois) / ((1 + taux_interet)**duree_mois - 1)
    else:
        mensualite = montant_pret / duree_mois
    
    tableau_amortissement = []
    capital_restant = montant_pret
    total_interets = 0
    
    for mois in range(1, duree_mois + 1):
        interets = capital_restant * taux_interet
        capital = mensualite - interets
        capital_restant -= capital
        total_interets += interets
        
        tableau_amortissement.append({
            'mois': mois,
            'mensualite': mensualite,
            'capital': capital,
            'interets': interets,
            'capital_restant': max(0, capital_restant)
        })
    
    return {
        'montant_pret': montant_pret,
        'mensualite': mensualite,
        'total_interets': total_interets,
        'cout_total': montant_pret + total_interets,
        'tableau_amortissement': tableau_amortissement,
        'recommandations': [
            f"Mensualité: {mensualite:,.0f} FCFA",
            f"Coût total du crédit: {total_interets:,.0f} FCFA",
            f"Montant total à rembourser: {montant_pret + total_interets:,.0f} FCFA"
        ]
    }

def calculate_bond_pricing(params):
    """Calcul évaluation d'obligations"""
    # Implémentation simplifiée pour la démo
    return {
        'message': 'Modèle d\'évaluation d\'obligations calculé',
        'parametres': params,
        'recommandations': ['Évaluation d\'obligations en cours de développement']
    }

def calculate_black_scholes(params):
    """Calcul Black-Scholes"""
    # Implémentation simplifiée pour la démo
    return {
        'message': 'Modèle Black-Scholes calculé',
        'parametres': params,
        'recommandations': ['Modèle Black-Scholes en cours de développement']
    }

def calculate_financial_ratios(params):
    """Calcul ratios financiers"""
    actif_total = float(params.get('actif_total', 1000000))
    passif_total = float(params.get('passif_total', 600000))
    chiffre_affaires = float(params.get('chiffre_affaires', 2000000))
    benefice_net = float(params.get('benefice_net', 100000))
    capitaux_propres = actif_total - passif_total
    
    ratios = {
        'ratio_endettement': passif_total / actif_total,
        'ratio_autonomie': capitaux_propres / actif_total,
        'rentabilite_actif': benefice_net / actif_total,
        'rentabilite_capitaux': benefice_net / capitaux_propres if capitaux_propres > 0 else 0,
        'marge_nette': benefice_net / chiffre_affaires if chiffre_affaires > 0 else 0
    }
    
    return {
        'ratios': ratios,
        'analyse': {
            'endettement': 'Élevé' if ratios['ratio_endettement'] > 0.6 else 'Modéré' if ratios['ratio_endettement'] > 0.3 else 'Faible',
            'rentabilite': 'Bonne' if ratios['rentabilite_actif'] > 0.1 else 'Moyenne' if ratios['rentabilite_actif'] > 0.05 else 'Faible'
        },
        'recommandations': [
            f"Ratio d'endettement: {ratios['ratio_endettement']*100:.1f}%",
            f"Rentabilité des actifs: {ratios['rentabilite_actif']*100:.1f}%",
            f"Marge nette: {ratios['marge_nette']*100:.1f}%"
        ]
    }

def calculate_real_estate_valuation(params):
    """Calcul évaluation immobilière"""
    # Implémentation simplifiée pour la démo
    return {
        'message': 'Modèle d\'évaluation immobilière calculé',
        'parametres': params,
        'recommandations': ['Évaluation immobilière en cours de développement']
    }

def calculate_lbo_analysis(params):
    """Calcul analyse LBO"""
    # Implémentation simplifiée pour la démo
    return {
        'message': 'Modèle d\'analyse LBO calculé',
        'parametres': params,
        'recommandations': ['Analyse LBO en cours de développement']
    }

def calculate_merger_analysis(params):
    """Calcul analyse fusion-acquisition"""
    # Implémentation simplifiée pour la démo
    return {
        'message': 'Modèle d\'analyse de fusion-acquisition calculé',
        'parametres': params,
        'recommandations': ['Analyse M&A en cours de développement']
    }

def generate_export(model, format_type):
    """Génère un export PDF ou Excel (simulation)"""
    # Ici nous implémenterons la vraie génération d'exports
    return {
        'url': f'/api/exports/{model.id}.{format_type}',
        'format': format_type,
        'generated_at': datetime.utcnow().isoformat()
    }

