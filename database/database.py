import sqlite3
import os
from datetime import datetime
import secrets

BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASEDIR, 'instance', 'civicai.db')


def get_db():
    """Get database connection"""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Initialize database with schema"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    db = get_db()
    cursor = db.cursor()

    schema_path = os.path.join(BASEDIR, 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        cursor.executescript(f.read())

    # Add duplicate_of column to existing databases
    cursor.execute("PRAGMA table_info(complaints)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'duplicate_of' not in columns:
        cursor.execute("""
            ALTER TABLE complaints
            ADD COLUMN duplicate_of TEXT
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_complaint_duplicate_of
        ON complaints(duplicate_of)
    """)

    db.commit()
    db.close()


def add_demo_data():
    """Add demo users and complaints"""
    from werkzeug.security import generate_password_hash
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if demo data already exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        return  # Demo data already added
    
    # Demo admin
    admin_password = generate_password_hash('admin123')
    cursor.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, ('Admin User', 'admin@civicai.com', admin_password, 'admin'))
    
    # Demo citizens
    citizen1_password = generate_password_hash('citizen123')
    cursor.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, ('Rajesh Kumar', 'rajesh@civicai.com', citizen1_password, 'citizen'))
    
    citizen2_password = generate_password_hash('citizen123')
    cursor.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, ('Priya Singh', 'priya@civicai.com', citizen2_password, 'citizen'))
    
    db.commit()
    
    # Demo complaints
    demo_complaints = [
        {
            'complaint_id': 'CMP-' + secrets.token_hex(4).upper(),
            'user_id': 2,
            'title': 'Large pothole near college gate',
            'description': 'Large pothole near the college gate causing danger to students. Students have had accidents. Immediate action needed.',
            'category': 'Pothole/Road Damage',
            'priority': 'Critical',
            'priority_reason': 'Safety hazard causing student accidents',
            'department': 'Roads Department',
            'latitude': 28.6179,
            'longitude': 77.2050,
            'address': 'College Gate Main Road, Delhi',
            'image_path': None,
            'status': 'In Progress',
            'admin_remarks': 'Assigned to repair team. Work started.'
        },
        {
            'complaint_id': 'CMP-' + secrets.token_hex(4).upper(),
            'user_id': 2,
            'title': 'Broken streetlight on market street',
            'description': 'The streetlight on market street near the supermarket has been broken for 2 weeks. Dark area at night.',
            'category': 'Streetlight',
            'priority': 'High',
            'priority_reason': 'Safety concern - dark area at night',
            'department': 'Electrical Department',
            'latitude': 28.6089,
            'longitude': 77.2120,
            'address': 'Market Street, Delhi',
            'image_path': None,
            'status': 'Assigned',
            'admin_remarks': 'Assigned to Electrical Department'
        },
        {
            'complaint_id': 'CMP-' + secrets.token_hex(4).upper(),
            'user_id': 3,
            'title': 'Garbage overflowing in residential area',
            'description': 'Garbage bins are overflowing in residential block C. Waste is scattered everywhere. Please arrange immediate collection.',
            'category': 'Garbage/Waste',
            'priority': 'High',
            'priority_reason': 'Health hazard - overflowing garbage',
            'department': 'Sanitation Department',
            'latitude': 28.6250,
            'longitude': 77.2000,
            'address': 'Block C, Residential Area, Delhi',
            'image_path': None,
            'status': 'Resolved',
            'admin_remarks': 'Garbage collected and bins cleaned. Complaint resolved.',
            'resolved_at': datetime.now()
        },
        {
            'complaint_id': 'CMP-' + secrets.token_hex(4).upper(),
            'user_id': 3,
            'title': 'Water leakage from main pipe',
            'description': 'Water leaking from main water pipe near park entrance. Water is wasted and ground is wet.',
            'category': 'Water Leakage',
            'priority': 'Medium',
            'priority_reason': 'Resource waste and ground hazard',
            'department': 'Water Department',
            'latitude': 28.6300,
            'longitude': 77.2100,
            'address': 'Park Entrance, Delhi',
            'image_path': None,
            'status': 'Submitted',
            'admin_remarks': None
        },
        {
            'complaint_id': 'CMP-' + secrets.token_hex(4).upper(),
            'user_id': 2,
            'title': 'Drainage blocked - water accumulation',
            'description': 'Main drainage near crossing is blocked. Water accumulates during rain. Need immediate cleaning.',
            'category': 'Drainage',
            'priority': 'High',
            'priority_reason': 'Risk of waterlogging and disease',
            'department': 'Drainage Department',
            'latitude': 28.5950,
            'longitude': 77.2200,
            'address': 'Main Crossing, Delhi',
            'image_path': None,
            'status': 'In Progress',
            'admin_remarks': 'Drainage cleaning scheduled for tomorrow'
        },
        {
            'complaint_id': 'CMP-' + secrets.token_hex(4).upper(),
            'user_id': 3,
            'title': 'Traffic signal not working',
            'description': 'Traffic signal at busy intersection has been malfunctioning. Causing traffic congestion.',
            'category': 'Traffic/Safety',
            'priority': 'High',
            'priority_reason': 'Traffic hazard',
            'department': 'Traffic Department',
            'latitude': 28.6100,
            'longitude': 77.1950,
            'address': 'Main Intersection, Delhi',
            'image_path': None,
            'status': 'Assigned',
            'admin_remarks': 'Traffic Department will repair the signal'
        },
        {
            'complaint_id': 'CMP-' + secrets.token_hex(4).upper(),
            'user_id': 2,
            'title': 'Park bench broken',
            'description': 'One of the benches in the public park is broken. Elderly people cannot sit.',
            'category': 'Public Infrastructure',
            'priority': 'Low',
            'priority_reason': 'Non-urgent maintenance issue',
            'department': 'General Civic Department',
            'latitude': 28.6350,
            'longitude': 77.2050,
            'address': 'Public Park, Delhi',
            'image_path': None,
            'status': 'Submitted',
            'admin_remarks': None
        },
        {
            'complaint_id': 'CMP-' + secrets.token_hex(4).upper(),
            'user_id': 3,
            'title': 'Street sign damaged',
            'description': 'Direction sign on main street is damaged. Creates confusion for visitors.',
            'category': 'Public Infrastructure',
            'priority': 'Low',
            'priority_reason': 'Minor guidance issue',
            'department': 'General Civic Department',
            'latitude': 28.6200,
            'longitude': 77.2150,
            'address': 'Main Street, Delhi',
            'image_path': None,
            'status': 'Resolved',
            'admin_remarks': 'Sign replaced with new one',
            'resolved_at': datetime.now()
        },
        {
            'complaint_id': 'CMP-' + secrets.token_hex(4).upper(),
            'user_id': 2,
            'title': 'Illegal encroachment on footpath',
            'description': 'Vendor has illegally set up shop on the footpath blocking passage for pedestrians.',
            'category': 'Other',
            'priority': 'Medium',
            'priority_reason': 'Obstruction to pedestrian movement',
            'department': 'General Civic Department',
            'latitude': 28.6150,
            'longitude': 77.2080,
            'address': 'Market Area, Delhi',
            'image_path': None,
            'status': 'Assigned',
            'admin_remarks': 'Civic authority will address encroachment'
        },
        {
            'complaint_id': 'CMP-' + secrets.token_hex(4).upper(),
            'user_id': 3,
            'title': 'Multiple potholes on school road',
            'description': 'Several potholes on the road leading to school. Very dangerous for students walking.',
            'category': 'Pothole/Road Damage',
            'priority': 'Critical',
            'priority_reason': 'Student safety hazard',
            'department': 'Roads Department',
            'latitude': 28.6400,
            'longitude': 77.1900,
            'address': 'School Road, Delhi',
            'image_path': None,
            'status': 'Submitted',
            'admin_remarks': None
        }
    ]
    
    for complaint in demo_complaints:
        cursor.execute("""
            INSERT INTO complaints 
            (complaint_id, user_id, title, description, category, priority, priority_reason, 
             department, latitude, longitude, address, image_path, status, admin_remarks, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint['complaint_id'],
            complaint['user_id'],
            complaint['title'],
            complaint['description'],
            complaint['category'],
            complaint['priority'],
            complaint['priority_reason'],
            complaint['department'],
            complaint['latitude'],
            complaint['longitude'],
            complaint['address'],
            complaint['image_path'],
            complaint['status'],
            complaint['admin_remarks'],
            complaint.get('resolved_at')
        ))
    
    db.commit()
    db.close()


def query_db(query, args=(), one=False):
    """Execute query and return result"""
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    db.close()
    return (rv[0] if rv else None) if one else rv