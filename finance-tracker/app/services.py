import requests
from datetime import datetime, timezone, timedelta
from app.extensions import db
from app.models import Transaction, Category, ExchangeRate, Budget

class TransactionService:
    def get_all_by_user(self, user_id):
        return Transaction.query.filter(Transaction.user_id == user_id, Transaction.deleted_at.is_(None)).all()
    
    def create_transaction(self, user_id, category_id, amount, description, date=None):
        if not date:
            date = datetime.utcnow().date()
        transaction = Transaction(user_id=user_id, category_id=category_id, amount=amount, description=description, date=date)
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    def get_monthly_summary(self, user_id, year, month):
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.deleted_at.is_(None),
            db.extract('month', Transaction.date) == month,
            db.extract('year', Transaction.date) == year
        ).all()

        income = sum(t.amount for t in transactions if t.type == 'income')
        expense = sum(t.amount for t in transactions if t.type == 'expense')

        return {
            'income': float(income),
            'expense': float(expense),
            'balance': float(income - expense)
        }
    
    def get_category_totals(self, user_id, start, end):
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.deleted_at.is_(None),
            Transaction.date >= start,
            Transaction.date <= end,
            Transaction.type == 'expense'
        ).all()

        totals = {}
        for t in transactions:
            category_name = t.category.name
            totals[category_name] = totals.get(category_name, 0) + float(t.amount)
        
        return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))
    
    def export_csv(self, transactions):
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description'])

        for t in transactions:
            writer.writerow([t.date, t.type, t.category.name, t.amount, t.description])

        return output.getvalue()
    
    def soft_delete_transaction(self, transaction_id, user_id):
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first_or_404()
        transaction.deleted_at = datetime.utcnow()
        db.session.commit()
        return True
    
class CurrencyConverter(TransactionService):
    BASE_URL = 'https://api.exchangerate-api.com/v4/latest/GEL'
    CACHE_DURATION = timedelta(hours=1)

    def get_rates(self):
        response = requests.get(self.BASE_URL, timeout=5)
        response.raise_for_status()
        return response.json()['rates']

    def convert(self, amount, from_cur, to_cur):
        if from_cur == to_cur:
            return float(amount)

        rate = self._get_cached_rate(from_cur, to_cur)
        return float(amount) * rate
    
    def _get_cached_rate(self, from_cur, to_cur):
        cached = ExchangeRate.query.filter_by(base=from_cur, target=to_cur).first()

        if cached and (datetime.now(timezone.utc) - cached.fetched_at.replace(tzinfo=timezone.utc)) < self.CACHE_DURATION:
            return cached.rate

        # cache miss or expired — fetch fresh rates
        rates = self.get_rates()
        rate = rates.get(to_cur)

        if cached:
            cached.rate = rate
            cached.fetched_at = datetime.now(timezone.utc)
        else:
            cached = ExchangeRate(base=from_cur, target=to_cur, rate=rate, fetched_at=datetime.now(timezone.utc))
            db.session.add(cached)

        db.session.commit()
        return rate
    

class CategoryService:
    def get_all_by_user(self, user_id):
        return Category.query.filter_by(user_id=user_id).all()

    def create_category(self, user_id, name, cat_type, color='#6c757d'):
        category = Category(user_id=user_id, name=name, type=cat_type, color=color)
        db.session.add(category)
        db.session.commit()
        return category
    
    def update_category(self, category_id, user_id, name, cat_type, color):
        category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()
        category.name = name
        category.type = cat_type
        category.color = color
        db.session.commit()
        return category
    
    def delete_category(self, category_id, user_id):
        category = Category.query.filter_by(id=category_id, user_id=user_id).first_or_404()
        db.session.delete(category)
        db.session.commit()
        return True

class BudgetService:
    def get_all_by_user(self, user_id):
        return Budget.query.filter_by(user_id=user_id).all()
    
    def create_or_update_budget(self, user_id, category_id, amount, month, year):
        # Handle unique constraint safely
        budget = Budget.query.filter_by(user_id=user_id, category_id=category_id, month=month, year=year).first()
        if budget:
            budget.amount = amount
        else:
            budget = Budget(user_id=user_id, category_id=category_id, amount=amount, month=month, year=year)
            db.session.add(budget)
        
        db.session.commit()
        return budget
    
    def delete_budget(self, budget_id, user_id):
        budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first_or_404()
        db.session.delete(budget)
        db.session.commit()
        return True
    

