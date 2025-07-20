from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import enum

db = SQLAlchemy()

class AccountStatus(enum.Enum):
    DEMO = "demo"
    ACTIVE_MONTHLY = "active_monthly"
    ACTIVE_YEARLY = "active_yearly"
    SUSPENDED = "suspended"

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    account_status = db.Column(db.Enum(AccountStatus), default=AccountStatus.DEMO, nullable=False)
    free_exports_used = db.Column(db.Integer, default=0, nullable=False)
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relations
    financial_models = db.relationship('FinancialModel', backref='user', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can_export(self):
        if self.account_status in [AccountStatus.ACTIVE_MONTHLY, AccountStatus.ACTIVE_YEARLY]:
            return True
        return self.free_exports_used < 3

    def use_free_export(self):
        if self.account_status == AccountStatus.DEMO:
            self.free_exports_used += 1
            db.session.commit()

    def is_subscription_active(self):
        if self.subscription_end and datetime.utcnow() <= self.subscription_end:
            return True
        return False

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'account_status': self.account_status.value,
            'free_exports_used': self.free_exports_used,
            'subscription_start': self.subscription_start.isoformat() if self.subscription_start else None,
            'subscription_end': self.subscription_end.isoformat() if self.subscription_end else None,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class FinancialModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    model_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    parameters = db.Column(db.JSON, nullable=True)
    results = db.Column(db.JSON, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'description': self.description,
            'parameters': self.parameters,
            'results': self.results,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='pending', nullable=False)
    input_data = db.Column(db.JSON, nullable=True)
    output_data = db.Column(db.JSON, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'status': self.status,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'error_message': self.error_message,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class FinancialStatement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    statement_type = db.Column(db.String(100), nullable=False)  # balance_sheet, income_statement, cash_flow
    accounting_standard = db.Column(db.String(50), nullable=False)  # IFRS, SYSCOHADA, SYCEBNL
    currency = db.Column(db.String(10), default='FCFA', nullable=False)
    data = db.Column(db.JSON, nullable=False)
    anomalies = db.Column(db.JSON, nullable=True)
    notes = db.Column(db.JSON, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'statement_type': self.statement_type,
            'accounting_standard': self.accounting_standard,
            'currency': self.currency,
            'data': self.data,
            'anomalies': self.anomalies,
            'notes': self.notes,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }

