from functools import wraps
from flask import session, jsonify, redirect, url_for, request
from models.user import User

def login_required_api(f):
    """Decorator to enforce authentication for API JSON routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Authentication required. Please login.'}), 401
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            return jsonify({'success': False, 'error': 'Invalid or inactive session.'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required_api(f):
    """Decorator to enforce admin role for API JSON routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Authentication required.'}), 401
        user = User.query.get(user_id)
        if not user or not user.is_active or not user.is_admin:
            return jsonify({'success': False, 'error': 'Admin privilege required.'}), 403
        return f(*args, **kwargs)
    return decorated_function

def login_required_view(f):
    """Decorator to enforce authentication for HTML template views."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login', next=request.path))
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required_view(f):
    """Decorator to enforce admin role for HTML template views."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login', next=request.path))
        user = User.query.get(user_id)
        if not user or not user.is_active or not user.is_admin:
            return redirect(url_for('dashboard.dashboard_view'))
        return f(*args, **kwargs)
    return decorated_function
