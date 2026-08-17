from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, current_user
from database.db import db
from models.user import User
from services.auth_service import login_required_view, admin_required_view, login_required_api, admin_required_api

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Renders login page or processes login form submission."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an Administrator.', 'danger')
                return render_template('login.html')
            
            # Store in session
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name
            login_user(user)

            user.last_login = datetime.utcnow()
            db.session.commit()

            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.dashboard_view'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Renders user registration page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'analyst').strip().lower()

        if role not in ('admin', 'analyst'):
            role = 'analyst'

        if not username or not email or not password or not full_name:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return render_template('register.html')

        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            is_active=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Logs out user and clears session."""
    session.clear()
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required_view
def profile():
    """Displays user profile page."""
    user = User.query.get(session.get('user_id'))
    return render_template('profile.html', user=user)

@auth_bp.route('/admin')
@login_required_view
@admin_required_view
def admin_panel():
    """Displays administrative user management panel."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin.html', users=users)

# REST API Auth Endpoints
@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for JSON authentication."""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if user and user.check_password(password):
        if not user.is_active:
            return jsonify({'success': False, 'error': 'Account inactive.'}), 403

        session['user_id'] = user.user_id
        session['username'] = user.username
        session['role'] = user.role
        session['full_name'] = user.full_name
        login_user(user)

        user.last_login = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict()
        })

    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/auth/users', methods=['GET'])
@login_required_api
@admin_required_api
def api_list_users():
    """Lists all users for admin."""
    users = User.query.all()
    return jsonify({'success': True, 'users': [u.to_dict() for u in users]})

@auth_bp.route('/api/auth/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required_api
@admin_required_api
def api_toggle_user_status(user_id):
    """Toggles active/inactive status of a user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    if user.user_id == session.get('user_id'):
        return jsonify({'success': False, 'error': 'Cannot deactivate your own logged-in account'}), 400

    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': user.is_active})
