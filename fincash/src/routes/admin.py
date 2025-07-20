from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, UserRole, AccountStatus, Task, FinancialModel
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def require_admin(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentification requise'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != UserRole.ADMIN:
            return jsonify({'error': 'Accès administrateur requis'}), 403
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@require_admin
def get_dashboard():
    """Tableau de bord administrateur"""
    try:
        # Statistiques générales
        total_users = User.query.count()
        active_users = User.query.filter(User.account_status.in_([AccountStatus.ACTIVE_MONTHLY, AccountStatus.ACTIVE_YEARLY])).count()
        demo_users = User.query.filter_by(account_status=AccountStatus.DEMO).count()
        
        # Statistiques des tâches
        total_tasks = Task.query.count()
        completed_tasks = Task.query.filter_by(status='completed').count()
        pending_tasks = Task.query.filter_by(status='pending').count()
        
        # Statistiques des modèles financiers
        total_models = FinancialModel.query.count()
        
        # Revenus (simulation basée sur les abonnements actifs)
        monthly_subscribers = User.query.filter_by(account_status=AccountStatus.ACTIVE_MONTHLY).count()
        yearly_subscribers = User.query.filter_by(account_status=AccountStatus.ACTIVE_YEARLY).count()
        monthly_revenue = monthly_subscribers * 30000  # 30,000 FCFA
        yearly_revenue = yearly_subscribers * 200000   # 200,000 FCFA
        total_revenue = monthly_revenue + yearly_revenue
        
        # Activité récente (7 derniers jours)
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = User.query.filter(User.created_at >= week_ago).count()
        tasks_week = Task.query.filter(Task.created_at >= week_ago).count()
        
        return jsonify({
            'statistics': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'demo': demo_users,
                    'new_this_week': new_users_week
                },
                'tasks': {
                    'total': total_tasks,
                    'completed': completed_tasks,
                    'pending': pending_tasks,
                    'this_week': tasks_week
                },
                'models': {
                    'total': total_models
                },
                'revenue': {
                    'monthly_subscribers': monthly_subscribers,
                    'yearly_subscribers': yearly_subscribers,
                    'monthly_revenue': monthly_revenue,
                    'yearly_revenue': yearly_revenue,
                    'total_revenue': total_revenue
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du chargement du tableau de bord: {str(e)}'}), 500

@admin_bp.route('/users', methods=['GET'])
@require_admin
def get_users():
    """Liste des utilisateurs avec pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        
        query = User.query
        
        # Filtrage par recherche
        if search:
            query = query.filter(
                (User.username.contains(search)) |
                (User.email.contains(search))
            )
        
        # Filtrage par statut
        if status_filter and status_filter in [s.value for s in AccountStatus]:
            query = query.filter_by(account_status=AccountStatus(status_filter))
        
        # Pagination
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'pages': users.pages,
                'per_page': per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du chargement des utilisateurs: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@require_admin
def get_user_details(user_id):
    """Détails d'un utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Statistiques de l'utilisateur
        user_tasks = Task.query.filter_by(user_id=user_id).all()
        user_models = FinancialModel.query.filter_by(user_id=user_id).all()
        
        completed_tasks = [task for task in user_tasks if task.status == 'completed']
        pending_tasks = [task for task in user_tasks if task.status == 'pending']
        
        return jsonify({
            'user': user.to_dict(),
            'statistics': {
                'total_tasks': len(user_tasks),
                'completed_tasks': len(completed_tasks),
                'pending_tasks': len(pending_tasks),
                'total_models': len(user_models)
            },
            'recent_tasks': [task.to_dict() for task in user_tasks[-10:]],  # 10 dernières tâches
            'recent_models': [model.to_dict() for model in user_models[-5:]]  # 5 derniers modèles
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du chargement des détails utilisateur: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@require_admin
def update_user_status(user_id):
    """Mise à jour du statut d'un utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        new_status = data.get('status')
        if not new_status or new_status not in [s.value for s in AccountStatus]:
            return jsonify({'error': 'Statut invalide'}), 400
        
        old_status = user.account_status
        user.account_status = AccountStatus(new_status)
        
        # Mise à jour des dates d'abonnement si nécessaire
        if new_status in ['active_monthly', 'active_yearly']:
            user.subscription_start = datetime.utcnow()
            if new_status == 'active_monthly':
                user.subscription_end = datetime.utcnow() + timedelta(days=30)
            else:  # active_yearly
                user.subscription_end = datetime.utcnow() + timedelta(days=365)
        elif new_status in ['demo', 'suspended']:
            user.subscription_start = None
            user.subscription_end = None
        
        db.session.commit()
        
        return jsonify({
            'message': f'Statut utilisateur mis à jour de {old_status.value} vers {new_status}',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/reset-exports', methods=['POST'])
@require_admin
def reset_user_exports(user_id):
    """Réinitialise le compteur d'exports gratuits d'un utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        old_count = user.free_exports_used
        user.free_exports_used = 0
        db.session.commit()
        
        return jsonify({
            'message': f'Compteur d\'exports réinitialisé (était à {old_count})',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la réinitialisation: {str(e)}'}), 500

@admin_bp.route('/tasks', methods=['GET'])
@require_admin
def get_tasks():
    """Liste des tâches avec pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', '')
        user_id_filter = request.args.get('user_id', type=int)
        
        query = Task.query
        
        # Filtrage par statut
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # Filtrage par utilisateur
        if user_id_filter:
            query = query.filter_by(user_id=user_id_filter)
        
        # Pagination
        tasks = query.order_by(Task.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Enrichir avec les informations utilisateur
        tasks_data = []
        for task in tasks.items:
            task_dict = task.to_dict()
            user = User.query.get(task.user_id)
            task_dict['user'] = {'username': user.username, 'email': user.email} if user else None
            tasks_data.append(task_dict)
        
        return jsonify({
            'tasks': tasks_data,
            'pagination': {
                'page': page,
                'pages': tasks.pages,
                'per_page': per_page,
                'total': tasks.total,
                'has_next': tasks.has_next,
                'has_prev': tasks.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du chargement des tâches: {str(e)}'}), 500

@admin_bp.route('/analytics/usage', methods=['GET'])
@require_admin
def get_usage_analytics():
    """Analytiques d'utilisation"""
    try:
        # Utilisation par type de modèle
        model_usage = db.session.query(
            FinancialModel.model_type,
            func.count(FinancialModel.id).label('count')
        ).group_by(FinancialModel.model_type).all()
        
        # Activité par mois (6 derniers mois)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        monthly_activity = db.session.query(
            func.date_trunc('month', Task.created_at).label('month'),
            func.count(Task.id).label('tasks')
        ).filter(Task.created_at >= six_months_ago).group_by('month').all()
        
        # Taux de conversion (demo vers payant)
        total_demo = User.query.filter_by(account_status=AccountStatus.DEMO).count()
        total_paid = User.query.filter(User.account_status.in_([AccountStatus.ACTIVE_MONTHLY, AccountStatus.ACTIVE_YEARLY])).count()
        conversion_rate = (total_paid / (total_demo + total_paid)) * 100 if (total_demo + total_paid) > 0 else 0
        
        return jsonify({
            'model_usage': [{'type': usage[0], 'count': usage[1]} for usage in model_usage],
            'monthly_activity': [{'month': activity[0].isoformat(), 'tasks': activity[1]} for activity in monthly_activity],
            'conversion': {
                'demo_users': total_demo,
                'paid_users': total_paid,
                'conversion_rate': round(conversion_rate, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du chargement des analytiques: {str(e)}'}), 500

@admin_bp.route('/system/health', methods=['GET'])
@require_admin
def system_health():
    """État de santé du système"""
    try:
        # Vérifications de base
        db_status = 'OK'
        try:
            db.session.execute('SELECT 1')
        except:
            db_status = 'ERROR'
        
        # Statistiques de performance
        avg_task_completion = db.session.query(
            func.avg(func.extract('epoch', Task.completed_at - Task.created_at))
        ).filter(Task.status == 'completed').scalar()
        
        return jsonify({
            'status': 'OK' if db_status == 'OK' else 'WARNING',
            'database': db_status,
            'performance': {
                'avg_task_completion_seconds': avg_task_completion or 0
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

