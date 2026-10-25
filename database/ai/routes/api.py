"""API endpoints"""

from flask import Blueprint, request, jsonify, session
from database.database import get_db
from functools import wraps

api_bp = Blueprint('api', __name__, url_prefix='/api')


def require_auth(f):
    """Decorator to check authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/complaints/map')
def get_map_complaints():
    """Get complaints for map visualization"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT id, complaint_id, category, priority, status, 
               latitude, longitude, title, description, address
        FROM complaints
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    
    complaints = cursor.fetchall()
    db.close()
    
    # Convert to JSON-serializable format
    data = []
    for complaint in complaints:
        data.append({
            'id': complaint['id'],
            'complaint_id': complaint['complaint_id'],
            'category': complaint['category'],
            'priority': complaint['priority'],
            'status': complaint['status'],
            'latitude': complaint['latitude'],
            'longitude': complaint['longitude'],
            'title': complaint['title'],
            'description': complaint['description'],
            'address': complaint['address']
        })
    
    return jsonify(data)


@api_bp.route('/complaints/<complaint_id>')
@require_auth
def get_complaint(complaint_id):
    """Get complaint details"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT * FROM complaints WHERE complaint_id = ?
    """, (complaint_id,))
    
    complaint = cursor.fetchone()
    db.close()
    
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404
    
    return jsonify(dict(complaint))


@api_bp.route('/dashboard/stats')
@require_auth
def get_dashboard_stats():
    """Get dashboard statistics"""
    db = get_db()
    cursor = db.cursor()
    
    if session.get('user_role') == 'admin':
        # Admin stats
        cursor.execute("SELECT COUNT(*) as total FROM complaints")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as pending FROM complaints WHERE status IN ('Submitted', 'Assigned')")
        pending = cursor.fetchone()['pending']
        
        cursor.execute("SELECT COUNT(*) as in_progress FROM complaints WHERE status = 'In Progress'")
        in_progress = cursor.fetchone()['in_progress']
        
        cursor.execute("SELECT COUNT(*) as resolved FROM complaints WHERE status = 'Resolved'")
        resolved = cursor.fetchone()['resolved']
    else:
        # Citizen stats
        user_id = session['user_id']
        cursor.execute("SELECT COUNT(*) as total FROM complaints WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as pending FROM complaints WHERE user_id = ? AND status IN ('Submitted', 'Assigned')", (user_id,))
        pending = cursor.fetchone()['pending']
        
        cursor.execute("SELECT COUNT(*) as in_progress FROM complaints WHERE user_id = ? AND status = 'In Progress'", (user_id,))
        in_progress = cursor.fetchone()['in_progress']
        
        cursor.execute("SELECT COUNT(*) as resolved FROM complaints WHERE user_id = ? AND status = 'Resolved'", (user_id,))
        resolved = cursor.fetchone()['resolved']
    
    db.close()
    
    return jsonify({
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved
    })