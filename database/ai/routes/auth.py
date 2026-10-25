"""Authentication routes"""

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import get_db
import re

auth_bp = Blueprint('auth', __name__)


def is_email_valid(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'citizen')
        
        errors = []
        
        # Validation
        if not name:
            errors.append('Name is required')
        if not email:
            errors.append('Email is required')
        elif not is_email_valid(email):
            errors.append('Invalid email format')
        if not password:
            errors.append('Password is required')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters')
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if not errors:
            db = get_db()
            cursor = db.cursor()
            
            # Check if email exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                errors.append('Email already registered')
            else:
                # Insert new user
                hashed_password = generate_password_hash(password)
                try:
                    cursor.execute("""
                        INSERT INTO users (name, email, password, role)
                        VALUES (?, ?, ?, ?)
                    """, (name, email, hashed_password, role))
                    db.commit()
                    db.close()
                    
                    return redirect(url_for('auth.login'))
                except Exception as e:
                    errors.append(f'Registration failed: {str(e)}')
                    db.close()
        
        return render_template('register.html', errors=errors)
    
    return render_template('register.html', errors=[])


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login user"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        errors = []
        
        if not email or not password:
            errors.append('Email and password are required')
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id, name, email, password, role FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            db.close()
            
            if user and check_password_hash(user['password'], password):
                session.permanent = True
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                session['user_role'] = user['role']
                
                # Redirect based on role
                if user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('citizen.dashboard'))
            else:
                errors.append('Invalid email or password')
        
        return render_template('login.html', errors=errors)
    
    return render_template('login.html', errors=[])


@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))