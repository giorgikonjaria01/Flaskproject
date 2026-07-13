from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from app.models import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # If the request is destined for the API, return JSON instead of a redirect
            if request.path.startswith('/api'):
                return jsonify({'error': 'Unauthorized. Authentication required.'}), 401
                
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    user_id = session.get('user_id')
    if user_id is None:
        return None
    return User.query.get(user_id)