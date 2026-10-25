"""Citizen routes"""

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from database.database import get_db
from ai.complaint_analyzer import analyze_complaint
from werkzeug.utils import secure_filename
import os
import secrets
from datetime import datetime
from functools import wraps

citizen_bp = Blueprint('citizen', __name__, url_prefix='/citizen')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def citizen_required(f):
    """Decorator to check if user is citizen"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'citizen':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@citizen_bp.route('/dashboard')
@citizen_required
def dashboard():
    """Citizen dashboard"""
    db = get_db()
    cursor = db.cursor()
    
    # Get stats
    user_id = session['user_id']
    
    cursor.execute("SELECT COUNT(*) as total FROM complaints WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as submitted FROM complaints WHERE user_id = ? AND status = 'Submitted'", (user_id,))
    submitted = cursor.fetchone()['submitted']
    
    cursor.execute("SELECT COUNT(*) as in_progress FROM complaints WHERE user_id = ? AND status = 'In Progress'", (user_id,))
    in_progress = cursor.fetchone()['in_progress']
    
    cursor.execute("SELECT COUNT(*) as resolved FROM complaints WHERE user_id = ? AND status = 'Resolved'", (user_id,))
    resolved = cursor.fetchone()['resolved']
    
    db.close()
    
    return render_template('citizen_dashboard.html',
                         total=total,
                         submitted=submitted,
                         in_progress=in_progress,
                         resolved=resolved)


@citizen_bp.route('/submit-complaint', methods=['GET', 'POST'])
@citizen_required
def submit_complaint():
    """Submit new complaint"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '')
        address = request.form.get('address', '').strip()
        latitude = request.form.get('latitude', '')
        longitude = request.form.get('longitude', '')
        
        errors = []
        image_path = None
        
        # Validation
        if not title:
            errors.append('Complaint title is required')
        if not description or len(description) < 20:
            errors.append('Description must be at least 20 characters')
        if not category:
            errors.append('Please select a category')
        if not address:
            errors.append('Address/Location is required')
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                if not allowed_file(file.filename):
                    errors.append('Only image files (PNG, JPG, JPEG, GIF, WEBP) are allowed')
                else:
                    # Save file with secure name
                    filename = secure_filename(file.filename)
                    filename = secrets.token_hex(8) + '_' + filename
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    image_path = f'uploads/{filename}'
        
        if not errors:
            # AI Analysis
            ai_result = analyze_complaint(title, description, image_path)
            
            # Generate complaint ID
            complaint_id = 'CMP-' + secrets.token_hex(4).upper()
            
            # Save to database
            db = get_db()
            cursor = db.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO complaints 
                    (complaint_id, user_id, title, description, category, priority, 
                     priority_reason, department, latitude, longitude, address, 
                     image_path, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    complaint_id,
                    session['user_id'],
                    title,
                    description,
                    ai_result['category'],
                    ai_result['priority'],
                    ai_result['priority_reason'],
                    ai_result['department'],
                    latitude if latitude else None,
                    longitude if longitude else None,
                    address,
                    image_path,
                    'Submitted'
                ))
                db.commit()
                db.close()
                
                return redirect(url_for('citizen.complaint_details', complaint_id=complaint_id))
            except Exception as e:
                errors.append(f'Error submitting complaint: {str(e)}')
                db.close()
        
        categories = [
            'Pothole/Road Damage',
            'Garbage/Waste',
            'Streetlight',
            'Water Leakage',
            'Drainage',
            'Traffic/Safety',
            'Public Infrastructure',
            'Other'
        ]
        
        return render_template('submit_complaint.html', 
                             categories=categories,
                             errors=errors,
                             form_data=request.form)
    
    categories = [
        'Pothole/Road Damage',
        'Garbage/Waste',
        'Streetlight',
        'Water Leakage',
        'Drainage',
        'Traffic/Safety',
        'Public Infrastructure',
        'Other'
    ]
    
    return render_template('submit_complaint.html', categories=categories, errors=[])


@citizen_bp.route('/my-complaints')
@citizen_required
def my_complaints():
    """View user's complaints"""
    db = get_db()
    cursor = db.cursor()
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    
    query = "SELECT * FROM complaints WHERE user_id = ?"
    params = [session['user_id']]
    
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    
    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    complaints = cursor.fetchall()
    db.close()
    
    # Get unique statuses and categories for filters
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT status FROM complaints WHERE user_id = ?", (session['user_id'],))
    statuses = [row['status'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT category FROM complaints WHERE user_id = ?", (session['user_id'],))
    categories = [row['category'] for row in cursor.fetchall()]
    db.close()
    
    return render_template('my_complaints.html',
                         complaints=complaints,
                         statuses=statuses,
                         categories=categories,
                         current_status=status_filter,
                         current_category=category_filter)


@citizen_bp.route('/complaint/<complaint_id>')
@citizen_required
def complaint_details(complaint_id):
    """View complaint details"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT * FROM complaints 
        WHERE complaint_id = ? AND user_id = ?
    """, (complaint_id, session['user_id']))
    
    complaint = cursor.fetchone()
    db.close()
    
    if not complaint:
        return render_template('404.html'), 404
    
    return render_template('complaint_details.html', complaint=complaint)