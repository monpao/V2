from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, FinancialStatement, Task
from datetime import datetime
import pandas as pd
import json
import io
import base64

financial_statements_bp = Blueprint('financial_statements', __name__)

def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentification requise'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@financial_statements_bp.route('/upload-balance', methods=['POST'])
@require_auth
def upload_balance_sheet():
    """Upload et traitement d'une balance comptable"""
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Vérifier si l'utilisateur peut effectuer cette opération
        if not user.can_export():
            return jsonify({
                'error': 'Limite d\'exportation atteinte. Veuillez souscrire à un abonnement.',
                'upgrade_required': True
            }), 403
        
        # Récupérer le fichier uploadé
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        # Récupérer les paramètres
        accounting_standard = request.form.get('accounting_standard', 'SYSCOHADA')
        currency = request.form.get('currency', 'FCFA')
        statement_name = request.form.get('name', f'État financier - {datetime.now().strftime("%Y-%m-%d")}')
        
        if accounting_standard not in ['IFRS', 'SYSCOHADA', 'SYCEBNL']:
            return jsonify({'error': 'Norme comptable non supportée'}), 400
        
        # Traiter le fichier selon son type
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        if file_extension == 'xlsx' or file_extension == 'xls':
            balance_data = process_excel_balance(file)
        elif file_extension == 'pdf':
            balance_data = process_pdf_balance(file)
        else:
            return jsonify({'error': 'Format de fichier non supporté. Utilisez Excel ou PDF.'}), 400
        
        if not balance_data:
            return jsonify({'error': 'Impossible de traiter le fichier. Vérifiez le format.'}), 400
        
        # Créer une tâche pour le traitement
        task = Task(
            task_type='financial_statement_generation',
            status='processing',
            input_data={
                'accounting_standard': accounting_standard,
                'currency': currency,
                'balance_data': balance_data
            },
            user_id=user_id
        )
        db.session.add(task)
        db.session.commit()
        
        # Générer les états financiers
        financial_statements = generate_financial_statements(balance_data, accounting_standard, currency)
        
        # Détecter les anomalies
        anomalies = detect_anomalies(balance_data, financial_statements, accounting_standard)
        
        # Générer les notes annexes
        notes = generate_notes(financial_statements, accounting_standard)
        
        # Sauvegarder l'état financier
        statement = FinancialStatement(
            name=statement_name,
            statement_type='complete',
            accounting_standard=accounting_standard,
            currency=currency,
            data=financial_statements,
            anomalies=anomalies,
            notes=notes,
            user_id=user_id
        )
        db.session.add(statement)
        
        # Mettre à jour la tâche
        task.status = 'completed'
        task.output_data = {
            'statement_id': statement.id,
            'anomalies_count': len(anomalies),
            'notes_count': len(notes)
        }
        task.completed_at = datetime.utcnow()
        
        # Utiliser un export gratuit si en mode démo
        if user.account_status.value == 'demo':
            user.use_free_export()
        
        db.session.commit()
        
        return jsonify({
            'message': 'États financiers générés avec succès',
            'statement': statement.to_dict(),
            'task_id': task.id,
            'anomalies_count': len(anomalies),
            'notes_count': len(notes),
            'remaining_free_exports': 3 - user.free_exports_used if user.account_status.value == 'demo' else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors du traitement: {str(e)}'}), 500

@financial_statements_bp.route('/statements', methods=['GET'])
@require_auth
def get_user_statements():
    """Récupère les états financiers de l'utilisateur"""
    user_id = session['user_id']
    statements = FinancialStatement.query.filter_by(user_id=user_id).order_by(FinancialStatement.created_at.desc()).all()
    
    return jsonify({
        'statements': [statement.to_dict() for statement in statements]
    }), 200

@financial_statements_bp.route('/statements/<int:statement_id>', methods=['GET'])
@require_auth
def get_statement(statement_id):
    """Récupère un état financier spécifique"""
    user_id = session['user_id']
    statement = FinancialStatement.query.filter_by(id=statement_id, user_id=user_id).first()
    
    if not statement:
        return jsonify({'error': 'État financier non trouvé'}), 404
    
    return jsonify({'statement': statement.to_dict()}), 200

@financial_statements_bp.route('/statements/<int:statement_id>/export', methods=['POST'])
@require_auth
def export_statement(statement_id):
    """Exporte un état financier en PDF ou Excel"""
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        statement = FinancialStatement.query.filter_by(id=statement_id, user_id=user_id).first()
        
        if not statement:
            return jsonify({'error': 'État financier non trouvé'}), 404
        
        if not user.can_export():
            return jsonify({
                'error': 'Limite d\'exportation atteinte. Veuillez souscrire à un abonnement.',
                'upgrade_required': True
            }), 403
        
        data = request.get_json()
        export_format = data.get('format', 'pdf')
        
        if export_format not in ['pdf', 'excel']:
            return jsonify({'error': 'Format d\'export non supporté'}), 400
        
        # Utiliser un export gratuit si en mode démo
        if user.account_status.value == 'demo':
            user.use_free_export()
        
        # Générer l'export
        export_result = generate_statement_export(statement, export_format)
        
        return jsonify({
            'message': 'Export généré avec succès',
            'export_url': export_result['url'],
            'remaining_free_exports': 3 - user.free_exports_used if user.account_status.value == 'demo' else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500

def process_excel_balance(file):
    """Traite un fichier Excel de balance comptable"""
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file.stream)
        
        # Normaliser les colonnes (rechercher les colonnes communes)
        columns_mapping = {}
        for col in df.columns:
            col_lower = str(col).lower()
            if 'compte' in col_lower or 'account' in col_lower:
                columns_mapping['account'] = col
            elif 'libelle' in col_lower or 'libellé' in col_lower or 'description' in col_lower:
                columns_mapping['description'] = col
            elif 'debit' in col_lower or 'débit' in col_lower:
                columns_mapping['debit'] = col
            elif 'credit' in col_lower or 'crédit' in col_lower:
                columns_mapping['credit'] = col
            elif 'solde' in col_lower or 'balance' in col_lower:
                columns_mapping['balance'] = col
        
        if not columns_mapping.get('account'):
            return None
        
        # Convertir en format standardisé
        balance_data = []
        for _, row in df.iterrows():
            try:
                account = str(row[columns_mapping['account']]).strip()
                if not account or account == 'nan':
                    continue
                
                description = str(row.get(columns_mapping.get('description', ''), '')).strip()
                debit = float(row.get(columns_mapping.get('debit', ''), 0) or 0)
                credit = float(row.get(columns_mapping.get('credit', ''), 0) or 0)
                balance = float(row.get(columns_mapping.get('balance', ''), debit - credit) or (debit - credit))
                
                balance_data.append({
                    'account': account,
                    'description': description,
                    'debit': debit,
                    'credit': credit,
                    'balance': balance
                })
            except (ValueError, TypeError):
                continue
        
        return balance_data
        
    except Exception as e:
        print(f"Erreur lors du traitement Excel: {e}")
        return None

def process_pdf_balance(file):
    """Traite un fichier PDF de balance comptable (simulation)"""
    # Pour l'instant, retourner des données simulées
    # Dans une vraie implémentation, on utiliserait des outils comme pdfplumber ou PyPDF2
    return [
        {'account': '101000', 'description': 'Capital social', 'debit': 0, 'credit': 1000000, 'balance': -1000000},
        {'account': '211000', 'description': 'Terrains', 'debit': 500000, 'credit': 0, 'balance': 500000},
        {'account': '411000', 'description': 'Clients', 'debit': 200000, 'credit': 0, 'balance': 200000},
        {'account': '512000', 'description': 'Banque', 'debit': 300000, 'credit': 0, 'balance': 300000}
    ]

def generate_financial_statements(balance_data, accounting_standard, currency):
    """Génère les états financiers à partir de la balance"""
    
    # Classifier les comptes selon la norme comptable
    account_classification = classify_accounts(balance_data, accounting_standard)
    
    # Générer le bilan
    balance_sheet = generate_balance_sheet(account_classification, currency)
    
    # Générer le compte de résultat
    income_statement = generate_income_statement(account_classification, currency)
    
    # Générer le tableau de flux de trésorerie (simplifié)
    cash_flow = generate_cash_flow_statement(account_classification, currency)
    
    return {
        'balance_sheet': balance_sheet,
        'income_statement': income_statement,
        'cash_flow_statement': cash_flow,
        'accounting_standard': accounting_standard,
        'currency': currency,
        'generation_date': datetime.utcnow().isoformat()
    }

def classify_accounts(balance_data, accounting_standard):
    """Classifie les comptes selon la norme comptable"""
    classification = {
        'assets': {'current': [], 'non_current': []},
        'liabilities': {'current': [], 'non_current': []},
        'equity': [],
        'revenues': [],
        'expenses': []
    }
    
    for account in balance_data:
        account_code = account['account']
        
        if accounting_standard == 'SYSCOHADA':
            classification = classify_syscohada_account(account, classification)
        elif accounting_standard == 'IFRS':
            classification = classify_ifrs_account(account, classification)
        elif accounting_standard == 'SYCEBNL':
            classification = classify_sycebnl_account(account, classification)
    
    return classification

def classify_syscohada_account(account, classification):
    """Classification selon SYSCOHADA"""
    code = account['account']
    
    if code.startswith('1'):  # Comptes de capitaux
        classification['equity'].append(account)
    elif code.startswith('2'):  # Comptes d'immobilisations
        classification['assets']['non_current'].append(account)
    elif code.startswith('3'):  # Comptes de stocks
        classification['assets']['current'].append(account)
    elif code.startswith('4'):  # Comptes de tiers
        if code.startswith('40') or code.startswith('42'):  # Fournisseurs
            classification['liabilities']['current'].append(account)
        else:  # Clients et autres
            classification['assets']['current'].append(account)
    elif code.startswith('5'):  # Comptes de trésorerie
        classification['assets']['current'].append(account)
    elif code.startswith('6'):  # Comptes de charges
        classification['expenses'].append(account)
    elif code.startswith('7'):  # Comptes de produits
        classification['revenues'].append(account)
    
    return classification

def classify_ifrs_account(account, classification):
    """Classification selon IFRS (similaire à SYSCOHADA pour cette démo)"""
    return classify_syscohada_account(account, classification)

def classify_sycebnl_account(account, classification):
    """Classification selon SYCEBNL (similaire à SYSCOHADA pour cette démo)"""
    return classify_syscohada_account(account, classification)

def generate_balance_sheet(classification, currency):
    """Génère le bilan"""
    
    # Actifs
    current_assets_total = sum(acc['balance'] for acc in classification['assets']['current'] if acc['balance'] > 0)
    non_current_assets_total = sum(acc['balance'] for acc in classification['assets']['non_current'] if acc['balance'] > 0)
    total_assets = current_assets_total + non_current_assets_total
    
    # Passifs
    current_liabilities_total = sum(abs(acc['balance']) for acc in classification['liabilities']['current'] if acc['balance'] < 0)
    non_current_liabilities_total = sum(abs(acc['balance']) for acc in classification['liabilities']['non_current'] if acc['balance'] < 0)
    total_liabilities = current_liabilities_total + non_current_liabilities_total
    
    # Capitaux propres
    equity_total = sum(abs(acc['balance']) for acc in classification['equity'] if acc['balance'] < 0)
    
    return {
        'assets': {
            'current_assets': {
                'total': current_assets_total,
                'details': classification['assets']['current']
            },
            'non_current_assets': {
                'total': non_current_assets_total,
                'details': classification['assets']['non_current']
            },
            'total': total_assets
        },
        'liabilities_and_equity': {
            'current_liabilities': {
                'total': current_liabilities_total,
                'details': classification['liabilities']['current']
            },
            'non_current_liabilities': {
                'total': non_current_liabilities_total,
                'details': classification['liabilities']['non_current']
            },
            'equity': {
                'total': equity_total,
                'details': classification['equity']
            },
            'total': total_liabilities + equity_total
        },
        'currency': currency
    }

def generate_income_statement(classification, currency):
    """Génère le compte de résultat"""
    
    total_revenues = sum(abs(acc['balance']) for acc in classification['revenues'] if acc['balance'] < 0)
    total_expenses = sum(acc['balance'] for acc in classification['expenses'] if acc['balance'] > 0)
    net_income = total_revenues - total_expenses
    
    return {
        'revenues': {
            'total': total_revenues,
            'details': classification['revenues']
        },
        'expenses': {
            'total': total_expenses,
            'details': classification['expenses']
        },
        'net_income': net_income,
        'currency': currency
    }

def generate_cash_flow_statement(classification, currency):
    """Génère le tableau de flux de trésorerie (simplifié)"""
    
    # Flux de trésorerie d'exploitation (approximation)
    operating_cash_flow = sum(acc['balance'] for acc in classification['revenues']) + sum(acc['balance'] for acc in classification['expenses'])
    
    # Flux de trésorerie d'investissement (approximation)
    investing_cash_flow = sum(acc['balance'] for acc in classification['assets']['non_current'])
    
    # Flux de trésorerie de financement (approximation)
    financing_cash_flow = sum(acc['balance'] for acc in classification['equity'])
    
    net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
    
    return {
        'operating_activities': operating_cash_flow,
        'investing_activities': investing_cash_flow,
        'financing_activities': financing_cash_flow,
        'net_cash_flow': net_cash_flow,
        'currency': currency
    }

def detect_anomalies(balance_data, financial_statements, accounting_standard):
    """Détecte les anomalies dans les états financiers"""
    anomalies = []
    
    # Vérification de l'équilibre du bilan
    balance_sheet = financial_statements['balance_sheet']
    assets_total = balance_sheet['assets']['total']
    liabilities_equity_total = balance_sheet['liabilities_and_equity']['total']
    
    if abs(assets_total - liabilities_equity_total) > 1:  # Tolérance de 1 unité
        anomalies.append({
            'type': 'balance_sheet_imbalance',
            'severity': 'high',
            'description': f'Le bilan n\'est pas équilibré. Actif: {assets_total}, Passif + Capitaux propres: {liabilities_equity_total}',
            'recommendation': 'Vérifiez la saisie des comptes et les soldes de la balance.'
        })
    
    # Vérification des soldes négatifs inappropriés
    for account in balance_data:
        code = account['account']
        balance = account['balance']
        
        # Les comptes d'actif ne devraient pas avoir de solde négatif
        if code.startswith(('2', '3', '4', '5')) and balance < 0:
            anomalies.append({
                'type': 'negative_asset_balance',
                'severity': 'medium',
                'description': f'Le compte {code} ({account["description"]}) a un solde négatif: {balance}',
                'recommendation': 'Vérifiez si ce solde négatif est justifié ou s\'il s\'agit d\'une erreur de saisie.'
            })
    
    # Vérification des ratios financiers
    if balance_sheet['assets']['total'] > 0:
        debt_ratio = balance_sheet['liabilities_and_equity']['current_liabilities']['total'] / balance_sheet['assets']['total']
        if debt_ratio > 0.8:
            anomalies.append({
                'type': 'high_debt_ratio',
                'severity': 'medium',
                'description': f'Ratio d\'endettement élevé: {debt_ratio:.2%}',
                'recommendation': 'Un ratio d\'endettement supérieur à 80% peut indiquer des difficultés financières.'
            })
    
    return anomalies

def generate_notes(financial_statements, accounting_standard):
    """Génère les notes annexes"""
    notes = []
    
    # Note sur les méthodes comptables
    notes.append({
        'title': 'Méthodes comptables',
        'content': f'Les états financiers ont été établis selon les normes {accounting_standard}. Les principales méthodes comptables appliquées sont conformes aux dispositions de cette norme.',
        'category': 'accounting_methods'
    })
    
    # Note sur les immobilisations
    non_current_assets = financial_statements['balance_sheet']['assets']['non_current_assets']['total']
    if non_current_assets > 0:
        notes.append({
            'title': 'Immobilisations',
            'content': f'Les immobilisations corporelles et incorporelles s\'élèvent à {non_current_assets:,.0f} et sont comptabilisées au coût historique.',
            'category': 'fixed_assets'
        })
    
    # Note sur la trésorerie
    notes.append({
        'title': 'Trésorerie et équivalents de trésorerie',
        'content': 'La trésorerie comprend les disponibilités en banque et en caisse.',
        'category': 'cash'
    })
    
    # Note sur les capitaux propres
    equity_total = financial_statements['balance_sheet']['liabilities_and_equity']['equity']['total']
    notes.append({
        'title': 'Capitaux propres',
        'content': f'Les capitaux propres s\'élèvent à {equity_total:,.0f} et comprennent le capital social et les réserves.',
        'category': 'equity'
    })
    
    return notes

def generate_statement_export(statement, format_type):
    """Génère un export d'état financier (simulation)"""
    return {
        'url': f'/api/exports/statement_{statement.id}.{format_type}',
        'format': format_type,
        'generated_at': datetime.utcnow().isoformat()
    }

