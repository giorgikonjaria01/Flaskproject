import requests
from datetime import datetime, timezone, timedelta
from app.extensions import db
from app.models import Transaction, Category, ExchangeRate

class TransactionService:
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