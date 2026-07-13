from flask import Blueprint, render_template
from app.auth.decorators import login_required, get_current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html')