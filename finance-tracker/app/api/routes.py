from flask import Blueprint, jsonify, request
from app.auth.decorators import login_required, get_current_user
from app.services import TransactionService, CategoryService
from datetime import datetime

api_bp = Blueprint('api', __name__)

cat_service = CategoryService()
tx_service = TransactionService()

@api_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions_api():
    user_id = get_current_user().id
    transactions = tx_service.get_all_by_user(user_id)
    return jsonify([{
        'id': t.id,
        'amount': float(t.amount),
        'description': t.description,
        'date': t.date.isoformat()
    } for t in transactions])

@api_bp.route('/transactions', methods=['POST'])
@login_required
def create_transaction_api():
    user_id = get_current_user().id
    data = request.get_json() or {}
    tx = tx_service.create_transaction(
        user_id=user_id,
        category_id=data.get('category_id'),
        amount=data.get('amount'),
        description=data.get('description')
    )
    return jsonify({'status': 'success', 'transaction_id': tx.id}), 201

@api_bp.route('/transactions/<int:id>', methods=['DELETE'])
@login_required
def delete_transaction_api(id):
    user_id = get_current_user().id
    tx_service.soft_delete_transaction(id, user_id)
    return jsonify({'status': 'deleted'}), 200

@api_bp.route('/balance', methods=['GET'])
@login_required
def get_balance_api():
    user_id = get_current_user().id
    now = datetime.utcnow()
    summary = tx_service.get_monthly_summary(user_id, now.year, now.month)
    return jsonify(summary), 200

@api_bp.route('/categories', methods=['GET'])
@login_required
def get_categories_api():
    user_id = get_current_user().id
    categories = cat_service.get_all_by_user(user_id)
    return jsonify([{
        'id': c.id, 'name': c.name, 'type': c.type, 'color': c.color
    } for c in categories]), 200