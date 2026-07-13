from datetime import datetime, timezone
from app.extensions import db

def utcnow():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    currency = db.Column(db.String(3), default='GEL', nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    
    # one-to-many
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    color = db.Column(db.String(7), default='#6c757d')

    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).date(), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True) # delete marker

    @property
    def is_deleted(self):
        return self.deleted_at is not None
    
class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    __table_args__ = ( db.UniqueConstraint('user_id', 'category_id', 'month', 'year', name='uq_budget_period'), ) 

class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'

    id = db.Column(db.Integer, primary_key=True)
    base = db.Column(db.String(3), nullable=False) # for example 'GEL'
    target = db.Column(db.String(3), nullable=False) # for example 'USD'
    rate = db.Column(db.Float, nullable=False)
    fetched_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    __table_args__ = ( db.UniqueConstraint('base', 'target', name='uq_currency_pair'), )
