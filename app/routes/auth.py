from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
import re

bp = Blueprint('auth', __name__)

def validate_password(password):
    """Ensure password meets minimum security standards."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        return "Password must contain both letters and numbers."
    return None

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('events.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        role = request.form.get('role', 'student')  # Default to student
        
        if not username or not email or not password:
            flash("All fields are required.")
            return redirect(url_for('auth.register'))

        # Validate password strength
        password_error = validate_password(password)
        if password_error:
            flash(password_error)
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Try logging in.')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/register/teacher', methods=['GET', 'POST'])
def register_teacher():
    if current_user.is_authenticated:
        return redirect(url_for('events.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        if not username or not email or not password:
            flash("All fields are required.")
            return redirect(url_for('auth.register_teacher'))
        
        password_error = validate_password(password)
        if password_error:
            flash(password_error)
            return redirect(url_for('auth.register_teacher'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.')
            return redirect(url_for('auth.register_teacher'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Try logging in.')
            return redirect(url_for('auth.register_teacher'))
        
        user = User(username=username, email=email, role='teacher')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Teacher registration successful! Please login.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_teacher.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('events.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            
            # Prevent Open Redirects (ensure next_page is a safe local URL)
            if next_page and not next_page.startswith('/'):
                next_page = None
            
            return redirect(next_page or url_for('events.index'))
        
        flash('Invalid username or password')
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
