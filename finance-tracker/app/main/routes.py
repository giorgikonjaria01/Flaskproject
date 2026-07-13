from flask import Response, render_template, request, redirect, url_for, flash, Blueprint
from app.auth.decorators import login_required, get_current_user
from app.services import TransactionService, CategoryService, BudgetService
from datetime import datetime

main_bp = Blueprint('main', __name__)

tx_service = TransactionService()
cat_service = CategoryService()
budget_service = BudgetService()

@main_bp.route('/')
def index():
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = get_current_user().id

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    type_filter = request.args.get('type_filter', '')

    pagination = tx_service.get_paginated(
        user_id, page=page, per_page=10,
        search=search, category_id=category_id, type_filter=type_filter
    )

    categories = cat_service.get_all_by_user(user_id)
    budgets = budget_service.get_all_by_user(user_id)

    now = datetime.utcnow()
    summary = tx_service.get_monthly_summary(user_id, now.year, now.month)

    # 80% budget warning check
    warnings = []
    category_totals = tx_service.get_category_totals(
        user_id,
        now.replace(day=1).date(),
        now.date()
    )
    for b in budgets:
        if b.month == now.month and b.year == now.year:
            spent = category_totals.get(b.category.name, 0)
            if spent >= float(b.amount) * 0.8:
                warnings.append(f"{b.category.name}: {spent:.2f} / {float(b.amount):.2f} (80%+ used)")
                flash(f'Warning: {b.category.name} budget is 80%+ used!', 'warning')


    warnings = budget_service.get_budget_warnings(user_id)

    for warning in warnings:
        flash(
        f"{warning['category']} budget is over 80% "
        f"({warning['spent']:.2f}/{warning['budget']:.2f})",
        "warning"
        )

    return render_template(
        'main/dashboard.html',
        pagination=pagination,
        transactions=pagination.items,
        categories=categories,
        budgets=budgets,
        summary=summary,
        warnings=warnings,
        search=search,
        category_id=category_id,
        type_filter=type_filter,
        budget_warnings=warnings
    )

# --- CATEGORY CRUD ---
@main_bp.route('/categories/create', methods=['POST'])
@login_required
def create_category():
    user_id = get_current_user().id
    name = request.form.get('name')
    cat_type = request.form.get('type')
    color = request.form.get('color', '#6c757d')
    
    cat_service.create_category(user_id, name, cat_type, color)
    flash('Category created successfully!')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    user_id = get_current_user().id
    cat_service.delete_category(id, user_id)
    flash('Category removed!')
    return redirect(url_for('main.dashboard'))

# --- TRANSACTION CRUD ---
@main_bp.route('/transactions/create', methods=['POST'])
@login_required
def create_transaction():
    user_id = get_current_user().id
    category_id = int(request.form.get('category_id'))
    amount = float(request.form.get('amount'))
    description = request.form.get('description')
    
    tx_service.create_transaction(user_id, category_id, amount, description)
    flash('Transaction recorded!')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/transactions/delete/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    user_id = get_current_user().id
    tx_service.soft_delete_transaction(id, user_id)
    flash('Transaction deleted!')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/transactions/export')
@login_required
def export_csv():
    user_id = get_current_user().id
    transactions = tx_service.get_all_by_user(user_id)
    csv_data = tx_service.export_csv(transactions)

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=transactions.csv'}
    )


@main_bp.route('/budgets/create', methods=['POST'])
@login_required
def create_budget():
    user_id = get_current_user().id
    category_id = int(request.form.get('category_id'))
    amount = float(request.form.get('amount'))
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))

    budget_service.create_or_update_budget(user_id, category_id, amount, month, year)
    flash('Budget saved!')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/budgets/delete/<int:id>', methods=['POST'])
@login_required
def delete_budget(id):
    user_id = get_current_user().id
    budget_service.delete_budget(id, user_id)
    flash('Budget removed!')
    return redirect(url_for('main.dashboard'))