"""Admin routes"""

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from database.database import get_db
from werkzeug.utils import secure_filename
import os
import secrets
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    db = get_db()
    cursor = db.cursor()
    
    # Total stats
    cursor.execute("SELECT COUNT(*) as total FROM complaints")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as submitted FROM complaints WHERE status = 'Submitted'")
    submitted = cursor.fetchone()['submitted']
    
    cursor.execute("SELECT COUNT(*) as in_progress FROM complaints WHERE status = 'In Progress'")
    in_progress = cursor.fetchone()['in_progress']
    
    cursor.execute("SELECT COUNT(*) as resolved FROM complaints WHERE status = 'Resolved'")
    resolved = cursor.fetchone()['resolved']
    
    cursor.execute("SELECT COUNT(*) as critical FROM complaints WHERE priority = 'Critical'")
    critical = cursor.fetchone()['critical']
    
    cursor.execute("SELECT COUNT(*) as high FROM complaints WHERE priority = 'High'")
    high = cursor.fetchone()['high']
    
    # Recent complaints
    cursor.execute("""
        SELECT c.*, u.name FROM complaints c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
        LIMIT 5
    """)
    recent = cursor.fetchall()
    
    # Category breakdown
    cursor.execute("""
        SELECT category, COUNT(*) as count FROM complaints
        GROUP BY category
        ORDER BY count DESC
    """)
    categories = cursor.fetchall()
    
    # Department breakdown
    cursor.execute("""
        SELECT department, COUNT(*) as count FROM complaints
        GROUP BY department
        ORDER BY count DESC
    """)
    departments = cursor.fetchall()
    
    db.close()
    
    return render_template('admin_dashboard.html',
                         total=total,
                         submitted=submitted,
                         in_progress=in_progress,
                         resolved=resolved,
                         critical=critical,
                         high=high,
                         recent=recent,
                         categories=categories,
                         departments=departments)


@admin_bp.route('/complaints')
@admin_required
def view_complaints():
    """View all complaints with filters"""
    db = get_db()
    cursor = db.cursor()
    
    # Get filters
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    priority_filter = request.args.get('priority', '')
    department_filter = request.args.get('department', '')
    search_query = request.args.get('search', '')
    
    query = "SELECT c.*, u.name FROM complaints c JOIN users u ON c.user_id = u.id WHERE 1=1"
    params = []
    
    if status_filter:
        query += " AND c.status = ?"
        params.append(status_filter)
    
    if category_filter:
        query += " AND c.category = ?"
        params.append(category_filter)
    
    if priority_filter:
        query += " AND c.priority = ?"
        params.append(priority_filter)
    
    if department_filter:
        query += " AND c.department = ?"
        params.append(department_filter)
    
    if search_query:
        query += " AND (c.complaint_id LIKE ? OR c.title LIKE ? OR c.description LIKE ?)"
        search_param = f"%{search_query}%"
        params.extend([search_param, search_param, search_param])
    
    query += " ORDER BY c.created_at DESC"
    
    cursor.execute(query, params)
    complaints = cursor.fetchall()
    
    # Get unique values for filters
    cursor.execute("SELECT DISTINCT status FROM complaints")
    statuses = [row['status'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT category FROM complaints")
    categories = [row['category'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT priority FROM complaints")
    priorities = [row['priority'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT department FROM complaints")
    departments = [row['department'] for row in cursor.fetchall()]
    
    db.close()
    
    return render_template('admin_complaints.html',
                         complaints=complaints,
                         statuses=statuses,
                         categories=categories,
                         priorities=priorities,
                         departments=departments,
                         current_status=status_filter,
                         current_category=category_filter,
                         current_priority=priority_filter,
                         current_department=department_filter,
                         search_query=search_query)


@admin_bp.route('/complaint/<complaint_id>')
@admin_required
def view_complaint(complaint_id):
    """View and edit complaint details"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT c.*, u.name, u.email FROM complaints c
        JOIN users u ON c.user_id = u.id
        WHERE c.complaint_id = ?
    """, (complaint_id,))
    
    complaint = cursor.fetchone()
    db.close()
    
    if not complaint:
        return render_template('404.html'), 404
    
    return render_template('admin_complaint_view.html', complaint=complaint)


@admin_bp.route('/complaint/<complaint_id>/update-status', methods=['POST'])
@admin_required
def update_status(complaint_id):
    """Update complaint status"""
    new_status = request.form.get('status')
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        UPDATE complaints 
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE complaint_id = ?
    """, (new_status, complaint_id))
    
    if new_status == 'Resolved':
        cursor.execute("""
            UPDATE complaints 
            SET resolved_at = CURRENT_TIMESTAMP
            WHERE complaint_id = ?
        """, (complaint_id,))
    
    db.commit()
    db.close()
    
    return redirect(url_for('admin.view_complaint', complaint_id=complaint_id))


@admin_bp.route('/complaint/<complaint_id>/add-remarks', methods=['POST'])
@admin_required
def add_remarks(complaint_id):
    """Add admin remarks to complaint"""
    remarks = request.form.get('remarks', '').strip()
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        UPDATE complaints 
        SET admin_remarks = ?, updated_at = CURRENT_TIMESTAMP
        WHERE complaint_id = ?
    """, (remarks, complaint_id))
    
    db.commit()
    db.close()
    
    return redirect(url_for('admin.view_complaint', complaint_id=complaint_id))


@admin_bp.route('/complaint/<complaint_id>/assign-department', methods=['POST'])
@admin_required
def assign_department(complaint_id):
    """Assign/change department for complaint"""
    department = request.form.get('department')
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        UPDATE complaints 
        SET department = ?, status = 'Assigned', updated_at = CURRENT_TIMESTAMP
        WHERE complaint_id = ?
    """, (department, complaint_id))
    
    db.commit()
    db.close()
    
    return redirect(url_for('admin.view_complaint', complaint_id=complaint_id))


@admin_bp.route('/complaint/<complaint_id>/upload-resolution', methods=['POST'])
@admin_required
def upload_resolution(complaint_id):
    """Upload resolution proof image"""
    if 'resolution_image' not in request.files:
        return redirect(url_for('admin.view_complaint', complaint_id=complaint_id))
    
    file = request.files['resolution_image']
    
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = secrets.token_hex(8) + '_' + filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        image_path = f'uploads/{filename}'
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            UPDATE complaints 
            SET resolution_image = ?, updated_at = CURRENT_TIMESTAMP
            WHERE complaint_id = ?
        """, (image_path, complaint_id))
        
        db.commit()
        db.close()
    
    return redirect(url_for('admin.view_complaint', complaint_id=complaint_id))


@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Admin analytics page"""
    db = get_db()
    cursor = db.cursor()
    
    # Category data
    cursor.execute("""
        SELECT category, COUNT(*) as count FROM complaints
        GROUP BY category
        ORDER BY count DESC
    """)
    category_data = cursor.fetchall()
    
    # Priority data
    cursor.execute("""
        SELECT priority, COUNT(*) as count FROM complaints
        GROUP BY priority
    """)
    priority_data = cursor.fetchall()
    
    # Department data
    cursor.execute("""
        SELECT department, COUNT(*) as count FROM complaints
        GROUP BY department
        ORDER BY count DESC
    """)
    department_data = cursor.fetchall()
    
    # Status distribution
    cursor.execute("""
        SELECT status, COUNT(*) as count FROM complaints
        GROUP BY status
    """)
    status_data = cursor.fetchall()
    
    # High priority complaints
    cursor.execute("""
        SELECT COUNT(*) as count FROM complaints WHERE priority IN ('High', 'Critical')
    """)
    high_priority_count = cursor.fetchone()['count']
    
    # Average resolution time (simple calculation)
    cursor.execute("""
        SELECT AVG(
            CAST((julianday(resolved_at) - julianday(created_at)) AS INTEGER)
        ) as avg_days
        FROM complaints
        WHERE resolved_at IS NOT NULL
    """)
    avg_resolution = cursor.fetchone()['avg_days']
    
    db.close()
    
    return render_template('analytics.html',
                         category_data=category_data,
                         priority_data=priority_data,
                         department_data=department_data,
                         status_data=status_data,
                         high_priority_count=high_priority_count,
                         avg_resolution=avg_resolution)