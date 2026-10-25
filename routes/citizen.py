"""
Citizen routes
"""

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for
)

from database.database import get_db
from ai.complaint_analyzer import analyze_complaint

from werkzeug.utils import secure_filename

import os
import secrets

from math import (
    radians,
    sin,
    cos,
    sqrt,
    atan2
)

from difflib import SequenceMatcher
from functools import wraps


citizen_bp = Blueprint(
    'citizen',
    __name__,
    url_prefix='/citizen'
)


UPLOAD_FOLDER = 'static/uploads'

ALLOWED_EXTENSIONS = {
    'png',
    'jpg',
    'jpeg',
    'gif',
    'webp'
}


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# CITIZEN AUTHENTICATION
# =========================================================

def citizen_required(f):

    @wraps(f)
    def decorated_function(
        *args,
        **kwargs
    ):

        if (
            'user_id' not in session
            or session.get('user_role') != 'citizen'
        ):

            return redirect(
                url_for('auth.login')
            )

        return f(
            *args,
            **kwargs
        )

    return decorated_function


# =========================================================
# FILE VALIDATION
# =========================================================

def allowed_file(filename):

    return (
        '.'
        in filename
        and filename.rsplit(
            '.',
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# DISTANCE CALCULATION
# =========================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371000

    lat1 = radians(
        float(lat1)
    )

    lon1 = radians(
        float(lon1)
    )

    lat2 = radians(
        float(lat2)
    )

    lon2 = radians(
        float(lon2)
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        +
        cos(lat1)
        *
        cos(lat2)
        *
        sin(dlon / 2) ** 2
    )

    c = (
        2
        *
        atan2(
            sqrt(a),
            sqrt(1 - a)
        )
    )

    return R * c


# =========================================================
# TEXT SIMILARITY
# =========================================================

def text_similarity(
    text1,
    text2
):

    text1 = text1.lower().strip()
    text2 = text2.lower().strip()

    return SequenceMatcher(
        None,
        text1,
        text2
    ).ratio()


# =========================================================
# DUPLICATE COMPLAINT DETECTION
# =========================================================

def find_duplicate_complaint(
    db,
    category,
    description,
    latitude,
    longitude
):

    if not latitude or not longitude:

        return None

    try:

        latitude = float(latitude)
        longitude = float(longitude)

    except (
        ValueError,
        TypeError
    ):

        return None

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT *
        FROM complaints
        WHERE category = ?
        AND latitude IS NOT NULL
        AND longitude IS NOT NULL
        AND status != 'Resolved'
        ORDER BY created_at DESC
        """,
        (category,)
    )

    complaints = cursor.fetchall()

    for complaint in complaints:

        distance = calculate_distance(
            latitude,
            longitude,
            complaint['latitude'],
            complaint['longitude']
        )

        # Same civic issue within 50 meters

        if distance <= 50:

            description_score = (
                text_similarity(
                    description,
                    complaint['description']
                )
            )

            if description_score >= 0.60:

                return complaint

    return None


# =========================================================
# DASHBOARD
# =========================================================

@citizen_bp.route('/dashboard')
@citizen_required
def dashboard():

    db = get_db()
    cursor = db.cursor()

    user_id = session['user_id']

    cursor.execute(
        """
        SELECT COUNT(*) as total
        FROM complaints
        WHERE user_id = ?
        """,
        (user_id,)
    )

    total = cursor.fetchone()['total']

    cursor.execute(
        """
        SELECT COUNT(*) as submitted
        FROM complaints
        WHERE user_id = ?
        AND status = 'Submitted'
        """,
        (user_id,)
    )

    submitted = cursor.fetchone()['submitted']

    cursor.execute(
        """
        SELECT COUNT(*) as in_progress
        FROM complaints
        WHERE user_id = ?
        AND status = 'In Progress'
        """,
        (user_id,)
    )

    in_progress = cursor.fetchone()['in_progress']

    cursor.execute(
        """
        SELECT COUNT(*) as resolved
        FROM complaints
        WHERE user_id = ?
        AND status = 'Resolved'
        """,
        (user_id,)
    )

    resolved = cursor.fetchone()['resolved']

    db.close()

    return render_template(
        'citizen_dashboard.html',
        total=total,
        submitted=submitted,
        in_progress=in_progress,
        resolved=resolved
    )


# =========================================================
# SUBMIT COMPLAINT
# =========================================================

@citizen_bp.route(
    '/submit-complaint',
    methods=['GET', 'POST']
)
@citizen_required
def submit_complaint():

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

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    if request.method == 'GET':

        return render_template(
            'submit_complaint.html',
            categories=categories,
            errors=[]
        )

    # -----------------------------------------------------
    # FORM DATA
    # -----------------------------------------------------

    description = request.form.get(
        'description',
        ''
    ).strip()

    category = request.form.get(
        'category',
        ''
    ).strip()

    address = request.form.get(
        'address',
        ''
    ).strip()

    latitude = request.form.get(
        'latitude',
        ''
    ).strip()

    longitude = request.form.get(
        'longitude',
        ''
    ).strip()

    errors = []

    image_path = None
    full_image_path = None

    # =====================================================
    # BASIC VALIDATION
    # =====================================================

    if (
        not description
        or len(description) < 20
    ):

        errors.append(
            'Description must be at least 20 characters.'
        )

    if not category:

        errors.append(
            'Please select a category.'
        )

    if not address:

        errors.append(
            'Address/Location is required.'
        )

    # =====================================================
    # IMAGE UPLOAD
    # =====================================================

    if 'image' in request.files:

        file = request.files['image']

        if file and file.filename:

            if not allowed_file(
                file.filename
            ):

                errors.append(
                    'Only image files '
                    '(PNG, JPG, JPEG, GIF, WEBP) '
                    'are allowed.'
                )

            else:

                filename = secure_filename(
                    file.filename
                )

                filename = (
                    secrets.token_hex(8)
                    + '_'
                    + filename
                )

                # Actual filesystem path

                full_image_path = os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )

                file.save(
                    full_image_path
                )

                # Path stored in database

                image_path = (
                    'uploads/'
                    + filename
                )

    # =====================================================
    # AI ANALYSIS
    # =====================================================

    if not errors:

        # IMPORTANT:
        # Send the REAL filesystem path to AI.

        ai_result = analyze_complaint(
            description,
            full_image_path,
            category
        )

        # =================================================
        # IMAGE VALIDATION
        # =================================================

        if (
            image_path
            and not ai_result.get(
                'image_valid',
                True
            )
        ):

            # Delete invalid image

            try:

                if (
                    full_image_path
                    and os.path.exists(
                        full_image_path
                    )
                ):

                    os.remove(
                        full_image_path
                    )

            except Exception as e:

                print(
                    f"Image cleanup error: {e}"
                )

            errors.append(
                '❌ Image rejected. '
                +
                ai_result.get(
                    'image_reason',
                    'The uploaded image does not match the selected civic issue.'
                )
            )

            image_path = None
            full_image_path = None

    # =====================================================
    # SAVE COMPLAINT
    # =====================================================

    if not errors:

        complaint_id = (
            'CMP-'
            +
            secrets.token_hex(4).upper()
        )

        db = get_db()
        cursor = db.cursor()

        # =================================================
        # DUPLICATE CHECK
        # =================================================

        duplicate_complaint = (
            find_duplicate_complaint(
                db,
                ai_result['category'],
                description,
                latitude,
                longitude
            )
        )

        duplicate_of = None

        if duplicate_complaint:

            duplicate_of = (
                duplicate_complaint['duplicate_of']
                if duplicate_complaint['duplicate_of']
                else duplicate_complaint['complaint_id']
            )

        try:

            cursor.execute(
                """
                INSERT INTO complaints
                (
                    complaint_id,
                    user_id,
                    title,
                    description,
                    category,
                    priority,
                    priority_reason,
                    department,
                    latitude,
                    longitude,
                    address,
                    image_path,
                    status,
                    duplicate_of
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    complaint_id,
                    session['user_id'],
                    ai_result['title'],
                    description,
                    ai_result['category'],
                    ai_result['priority'],
                    ai_result['priority_reason'],
                    ai_result['department'],
                    latitude if latitude else None,
                    longitude if longitude else None,
                    address,
                    image_path,
                    'Submitted',
                    duplicate_of
                )
            )

            db.commit()

            db.close()

            return redirect(
                url_for(
                    'citizen.complaint_details',
                    complaint_id=complaint_id
                )
            )

        except Exception as e:

            db.rollback()
            db.close()

            # Delete image if database insertion fails

            if full_image_path:

                try:

                    if os.path.exists(
                        full_image_path
                    ):

                        os.remove(
                            full_image_path
                        )

                except Exception as delete_error:

                    print(
                        f"Image cleanup error: "
                        f"{delete_error}"
                    )

            errors.append(
                f'Error submitting complaint: {str(e)}'
            )

    # =====================================================
    # SHOW FORM AGAIN
    # =====================================================

    return render_template(
        'submit_complaint.html',
        categories=categories,
        errors=errors,
        form_data=request.form
    )


# =========================================================
# MY COMPLAINTS
# =========================================================

@citizen_bp.route('/my-complaints')
@citizen_required
def my_complaints():

    db = get_db()
    cursor = db.cursor()

    status_filter = request.args.get(
        'status',
        ''
    )

    category_filter = request.args.get(
        'category',
        ''
    )

    query = (
        "SELECT * FROM complaints "
        "WHERE user_id = ?"
    )

    params = [
        session['user_id']
    ]

    if status_filter:

        query += " AND status = ?"

        params.append(
            status_filter
        )

    if category_filter:

        query += " AND category = ?"

        params.append(
            category_filter
        )

    query += (
        " ORDER BY created_at DESC"
    )

    cursor.execute(
        query,
        params
    )

    complaints = cursor.fetchall()

    db.close()

    # Get filter options

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT DISTINCT status
        FROM complaints
        WHERE user_id = ?
        """,
        (session['user_id'],)
    )

    statuses = [
        row['status']
        for row in cursor.fetchall()
    ]

    cursor.execute(
        """
        SELECT DISTINCT category
        FROM complaints
        WHERE user_id = ?
        """,
        (session['user_id'],)
    )

    categories = [
        row['category']
        for row in cursor.fetchall()
    ]

    db.close()

    return render_template(
        'my_complaints.html',
        complaints=complaints,
        statuses=statuses,
        categories=categories,
        current_status=status_filter,
        current_category=category_filter
    )


# =========================================================
# COMPLAINT DETAILS
# =========================================================

@citizen_bp.route(
    '/complaint/<complaint_id>'
)
@citizen_required
def complaint_details(
    complaint_id
):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT *
        FROM complaints
        WHERE complaint_id = ?
        AND user_id = ?
        """,
        (
            complaint_id,
            session['user_id']
        )
    )

    complaint = cursor.fetchone()

    db.close()

    if not complaint:

        return render_template(
            '404.html'
        ), 404

    return render_template(
        'complaint_details.html',
        complaint=complaint
    )