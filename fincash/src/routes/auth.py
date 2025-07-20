from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, UserRole, AccountStatus
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    # Au moins 8 caractères, une majuscule, une minuscule, un chiffre
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation des données
        if not username or len(username) < 3:
            return jsonify({'error': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Adresse email invalide'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre'}), 400
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Cette adresse email est déjà utilisée'}), 400
        
        # Créer le nouvel utilisateur
        user = User(
            username=username,
            email=email,
            role=UserRole.USER,
            account_status=AccountStatus.DEMO
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Compte créé avec succès',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la création du compte: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        username_or_email = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({'error': 'Nom d\'utilisateur/email et mot de passe requis'}), 400
        
        # Chercher l'utilisateur par nom d'utilisateur ou email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email.lower())
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Identifiants incorrects'}), 401
        
        # Mettre à jour la dernière connexion
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Créer la session
        session['user_id'] = user.id
        session['user_role'] = user.role.value
        
        return jsonify({
            'message': 'Connexion réussie',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la connexion: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Déconnexion réussie'}), 200

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            }), 200
    
    return jsonify({'authenticated': False}), 200

