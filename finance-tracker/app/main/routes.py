from flask import render_template, request, redirect, url_for, flash, Blueprint
from app.auth.decorators import login_required, get_current_user
from app.services import TransactionService, CategoryService, BudgetService

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
    # Pass the logged-in user's ID dynamically
    user_id = get_current_user().id 
    
    transactions = tx_service.get_all_by_user(user_id)
    categories = cat_service.get_all_by_user(user_id)
    budgets = budget_service.get_all_by_user(user_id)
    
    return render_template('main/dashboard.html', transactions=transactions, categories=categories, budgets=budgets)

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