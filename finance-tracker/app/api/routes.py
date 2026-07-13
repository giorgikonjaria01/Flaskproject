from datetime import datetime
from flask import Blueprint, jsonify, request
from app.auth.decorators import login_required, get_current_user
from app.services import TransactionService, CategoryService, CurrencyConverter

api_bp = Blueprint('api', __name__)

cat_service = CategoryService()
tx_service = TransactionService()
currency_service = CurrencyConverter()



@api_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions_api():

    user_id = get_current_user().id

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    category_id = request.args.get('category_id', type=int)
    type_filter = request.args.get('type')

    pagination = tx_service.get_paginated(
        user_id,
        page=page,
        per_page=10,
        search=search,
        category_id=category_id,
        type_filter=type_filter
    )

    return jsonify({
        "page": pagination.page,
        "pages": pagination.pages,
        "transactions": [
            {
                "id": t.id,
                "amount": float(t.amount),
                "type": t.type,
                "category": t.category.name,
                "description": t.description,
                "date": t.date.isoformat()
            }
            for t in pagination.items
        ]
    }), 200

@api_bp.route('/transactions/<int:id>', methods=['DELETE'])
@login_required
def delete_transaction_api(id):
    user_id = get_current_user().id
    transaction = tx_service.get_by_id(id, user_id)

    if not transaction:
        return jsonify({'error': 'transaction not found'}), 404

    tx_service.soft_delete_transaction(id, user_id)
    return '', 204

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


@api_bp.route('/convert', methods=['GET'])
@login_required
def convert_currency_api():
    amount = request.args.get('amount')
    from_cur = request.args.get('from', 'GEL')
    to_cur = request.args.get('to')

    if not amount or not to_cur:
        return jsonify({'error': 'amount and to are required'}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'amount must be a number'}), 400

    try:
        converted = currency_service.convert(amount, from_cur, to_cur)
    except Exception:
        return jsonify({'error': 'currency conversion failed'}), 502

    return jsonify({
        'original_amount': amount,
        'from': from_cur,
        'to': to_cur,
        'converted_amount': round(converted, 2)
    }), 200