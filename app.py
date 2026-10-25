"""
CivicAI - Smart City Complaint Management System
Main Flask Application
"""

import os
from flask import Flask, render_template, redirect, url_for, session
from dotenv import load_dotenv
from config import config
from database.database import init_db, add_demo_data, get_db
from routes.auth import auth_bp
from routes.citizen import citizen_bp
from routes.admin import admin_bp
from routes.api import api_bp
from ai.chatbot import get_assistant

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])
print("GEMINI KEY LOADED:", bool(app.config.get('GEMINI_API_KEY')))
print("USE GEMINI:", app.config.get('USE_GEMINI'))

# Ensure instance folder exists
os.makedirs('instance', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

# Initialize database
with app.app_context():
    init_db()
    add_demo_data()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(citizen_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)

# Initialize AI assistant
ai_assistant = get_assistant(
    use_gemini=app.config['USE_GEMINI'],
    api_key=app.config['GEMINI_API_KEY']
)


# Routes
@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/api/chatbot/chat', methods=['POST'])
def chatbot_chat():
    """Chatbot API endpoint"""
    from flask import request, jsonify
    
    data = request.get_json()
    message = data.get('message', '')
    
    response = ai_assistant.get_response(message)
    
    return jsonify(response)


# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return render_template('404.html'), 500


@app.before_request
def load_logged_in_user():
    """Load user info into session"""
    pass


@app.context_processor
def inject_user():
    """Inject user into template context"""
    if 'user_id' in session:
        return {
            'current_user': {
                'id': session.get('user_id'),
                'name': session.get('user_name'),
                'role': session.get('user_role')
            }
        }
    return {}


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )