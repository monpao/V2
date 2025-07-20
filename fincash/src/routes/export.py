from flask import Blueprint, request, jsonify, send_file, session
from src.models.user import db, User
from src.export_engine import FinancialExportEngine
from src.financial_engine import FinancialEngine
from src.ai_advisor import AIFinancialAdvisor
import os
import tempfile
from datetime import datetime

export_bp = Blueprint('export', __name__)
export_engine = FinancialExportEngine()
modeling_engine = FinancialEngine()
ai_advisor = AIFinancialAdvisor()

@export_bp.route('/model/<int:model_id>/pdf', methods=['GET'])
def export_model_pdf(model_id):
    """Exporte un modèle financier en PDF"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Vérifier les droits d'export
    if not user.can_export():
        return jsonify({
            'error': 'Limite d\'exportation atteinte',
            'message': 'Vous avez utilisé vos 3 exportations gratuites. Passez à un abonnement payant pour des exportations illimitées.'
        }), 403
    
    try:
        # Récupérer les données du modèle (simulation pour la démo)
        model_data = {
            'results': {
                'VAN': 1250000,
                'TRI': 15.5,
                'Délai de récupération': 3.2,
                'Indice de rentabilité': 1.25
            },
            'cash_flows': [100000, 150000, 200000, 250000, 300000],
            'sensitivity_analysis': [800000, 1250000, 1800000],
            'summary': 'Analyse DCF montrant une rentabilité positive avec une VAN de 1,25M FCFA et un TRI de 15,5%.'
        }
        
        # Générer l'analyse IA
        ai_analysis = ai_advisor.analyze_financial_model('dcf', model_data)
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = export_engine.export_to_pdf(
                model_data, 
                'dcf', 
                ai_analysis, 
                tmp_file.name
            )
        
        # Utiliser un export gratuit si compte démo
        if user.account_status.value == 'demo':
            user.use_free_export()
        
        # Retourner le fichier
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'fincash_rapport_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export PDF: {str(e)}'}), 500

@export_bp.route('/model/<int:model_id>/excel', methods=['GET'])
def export_model_excel(model_id):
    """Exporte un modèle financier en Excel"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Vérifier les droits d'export
    if not user.can_export():
        return jsonify({
            'error': 'Limite d\'exportation atteinte',
            'message': 'Vous avez utilisé vos 3 exportations gratuites. Passez à un abonnement payant pour des exportations illimitées.'
        }), 403
    
    try:
        # Récupérer les données du modèle (simulation pour la démo)
        model_data = {
            'results': {
                'VAN': 1250000,
                'TRI': 15.5,
                'Délai de récupération': 3.2,
                'Indice de rentabilité': 1.25
            },
            'detailed_data': [
                {'Année': 0, 'Investissement': -1000000, 'Flux': -1000000, 'VAN Cumulée': -1000000},
                {'Année': 1, 'Investissement': 0, 'Flux': 100000, 'VAN Cumulée': -913043},
                {'Année': 2, 'Investissement': 0, 'Flux': 150000, 'VAN Cumulée': -783261},
                {'Année': 3, 'Investissement': 0, 'Flux': 200000, 'VAN Cumulée': -631401},
                {'Année': 4, 'Investissement': 0, 'Flux': 250000, 'VAN Cumulée': -460348},
                {'Année': 5, 'Investissement': 0, 'Flux': 300000, 'VAN Cumulée': 1250000}
            ]
        }
        
        # Générer l'analyse IA
        ai_analysis = ai_advisor.analyze_financial_model('dcf', model_data)
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            excel_path = export_engine.export_to_excel(
                model_data, 
                'dcf', 
                ai_analysis, 
                tmp_file.name
            )
        
        # Utiliser un export gratuit si compte démo
        if user.account_status.value == 'demo':
            user.use_free_export()
        
        # Retourner le fichier
        return send_file(
            excel_path,
            as_attachment=True,
            download_name=f'fincash_donnees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export Excel: {str(e)}'}), 500

@export_bp.route('/model/<int:model_id>/complete', methods=['GET'])
def export_model_complete(model_id):
    """Exporte un modèle financier en PDF et Excel (pack complet)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Vérifier les droits d'export (compte comme 1 export)
    if not user.can_export():
        return jsonify({
            'error': 'Limite d\'exportation atteinte',
            'message': 'Vous avez utilisé vos 3 exportations gratuites. Passez à un abonnement payant pour des exportations illimitées.'
        }), 403
    
    try:
        # Récupérer les données du modèle
        model_data = {
            'results': {
                'VAN': 1250000,
                'TRI': 15.5,
                'Délai de récupération': 3.2,
                'Indice de rentabilité': 1.25
            },
            'cash_flows': [100000, 150000, 200000, 250000, 300000],
            'sensitivity_analysis': [800000, 1250000, 1800000],
            'detailed_data': [
                {'Année': 0, 'Investissement': -1000000, 'Flux': -1000000, 'VAN Cumulée': -1000000},
                {'Année': 1, 'Investissement': 0, 'Flux': 100000, 'VAN Cumulée': -913043},
                {'Année': 2, 'Investissement': 0, 'Flux': 150000, 'VAN Cumulée': -783261},
                {'Année': 3, 'Investissement': 0, 'Flux': 200000, 'VAN Cumulée': -631401},
                {'Année': 4, 'Investissement': 0, 'Flux': 250000, 'VAN Cumulée': -460348},
                {'Année': 5, 'Investissement': 0, 'Flux': 300000, 'VAN Cumulée': 1250000}
            ],
            'summary': 'Analyse DCF montrant une rentabilité positive avec une VAN de 1,25M FCFA et un TRI de 15,5%.'
        }
        
        # Générer l'analyse IA
        ai_analysis = ai_advisor.analyze_financial_model('dcf', model_data)
        
        # Créer un répertoire temporaire
        temp_dir = tempfile.mkdtemp()
        base_filename = os.path.join(temp_dir, f'fincash_rapport_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        # Générer les deux fichiers
        export_result = export_engine.generate_comprehensive_report(
            model_data, 
            'dcf', 
            ai_analysis, 
            base_filename
        )
        
        # Utiliser un export gratuit si compte démo
        if user.account_status.value == 'demo':
            user.use_free_export()
        
        return jsonify({
            'success': True,
            'message': 'Rapport complet généré avec succès',
            'files': {
                'pdf': export_result['pdf_path'],
                'excel': export_result['excel_path']
            },
            'generated_at': export_result['generated_at'],
            'remaining_exports': 3 - user.free_exports_used if user.account_status.value == 'demo' else 'illimité'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export complet: {str(e)}'}), 500

@export_bp.route('/user/export-status', methods=['GET'])
def get_export_status():
    """Récupère le statut d'export de l'utilisateur"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    if user.account_status.value == 'demo':
        return jsonify({
            'account_type': 'demo',
            'exports_used': user.free_exports_used,
            'exports_remaining': 3 - user.free_exports_used,
            'can_export': user.can_export(),
            'upgrade_required': not user.can_export()
        })
    else:
        return jsonify({
            'account_type': user.account_status.value,
            'exports_used': 'illimité',
            'exports_remaining': 'illimité',
            'can_export': True,
            'upgrade_required': False
        })

@export_bp.route('/demo/sample-export', methods=['GET'])
def demo_sample_export():
    """Génère un export de démonstration sans utiliser les quotas"""
    try:
        # Données de démonstration
        demo_data = {
            'results': {
                'VAN (FCFA)': 2500000,
                'TRI (%)': 18.5,
                'Délai de récupération (années)': 2.8,
                'Indice de rentabilité': 1.45
            },
            'cash_flows': [200000, 300000, 400000, 500000, 600000],
            'sensitivity_analysis': [1800000, 2500000, 3200000],
            'summary': 'Exemple d\'analyse DCF démontrant les capacités de Fincash avec une VAN positive de 2,5M FCFA.'
        }
        
        # Analyse IA de démonstration
        demo_ai_analysis = {
            'analysis': 'Cette analyse DCF présente des résultats très favorables avec une VAN positive significative et un TRI supérieur au coût du capital. Le projet génère de la valeur pour l\'entreprise.',
            'recommendations': [
                'Procéder à l\'investissement car la VAN est largement positive',
                'Surveiller les hypothèses de croissance des flux de trésorerie',
                'Considérer une analyse de sensibilité plus poussée sur le taux d\'actualisation'
            ],
            'risks': [
                'Risque de marché pouvant affecter les revenus projetés',
                'Risque de taux d\'intérêt impactant le coût du capital',
                'Risque opérationnel lié à l\'exécution du projet'
            ]
        }
        
        # Créer un fichier temporaire pour la démo
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = export_engine.export_to_pdf(
                demo_data, 
                'dcf', 
                demo_ai_analysis, 
                tmp_file.name
            )
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name='fincash_demo_rapport.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération de la démo: {str(e)}'}), 500

