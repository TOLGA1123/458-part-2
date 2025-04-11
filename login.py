from flask import Flask, render_template, redirect, url_for, session, request, jsonify
import re
from authlib.integrations.flask_client import OAuth
import os
import time
import uuid
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Dummy user storage (email/phone -> password)
users = {
    'admin@gmail.com': 'password123',
    'admin2@gmail.com': 'password123',
    '+1234567890': 'password123'
}

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id="1045716424808-g5ckn3rgeuj0h628f2acbershk2p5vc9.apps.googleusercontent.com",
    client_secret="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",
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth?hl=en",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "openid email profile"},
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs"
)

def is_valid_email(value):
    """Check if the input is a valid email format."""
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, value)

def is_valid_phone(value):
    """Check if the input is a valid phone number format (e.g., +1234567890)."""
    phone_regex = r"^\+?[0-9]{10,15}$"  # Allows optional '+' and 10-15 digits
    return re.match(phone_regex, value)

@app.route('/session_data')
def session_data():
    """Returns session data for testing"""
    if 'user' in session:
        return jsonify({"user": session['user']}), 200
    elif 'google_user' in session:
        return jsonify({"user": session['google_user']['email']}), 200
    return jsonify({"error": "No user logged in"}), 401


@app.route('/')
def home():
    """Home page that shows email/phone or Google user info."""
    if 'user' in session:
        return render_template('home.html', user=session['user'])
    elif 'google_user' in session:
        return render_template('home.html', user=session['google_user']['name'])
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Login function that accepts both email and phone numbers."""
    error = None
    if 'failed_attempts' not in session:
        session['failed_attempts'] = 0
    if 'lockout_time' not in session:
        session['lockout_time'] = None

    # Generate a unique session ID if it's not already present
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

    if request.method == 'POST':
        if session['lockout_time']:
            lockout_time = session['lockout_time']
            current_time = time.time()

            # If lockout time has passed, reset the failed attempts and lockout time
            if current_time > lockout_time:
                session['failed_attempts'] = 0
                session['lockout_time'] = None
            else:
                # If within the lockout period, show an error and return
                error = f"Too many failed attempts. Please try again in {int(lockout_time - current_time)} seconds."
                return render_template('login.html', error=error)
            
        # ✅ Get data from JSON
    data = request.get_json()
    user_input = data.get('user_input', '').strip()
    password = data.get('password', '')

    if not user_input and not password:
        error = "Email/Phone and Password are required."
    elif not user_input:
        error = "Email/Phone field is required."
    elif not password:
        error = "Password field is required."
    elif not (is_valid_email(user_input) or is_valid_phone(user_input)):
        error = "Invalid email or phone number format."
    elif user_input not in users:
        error = "Invalid credentials."
    elif users[user_input] != password:
        error = "Invalid credentials."

    if not error:
        session['user'] = user_input
        session['failed_attempts'] = 0
        session['lockout_time'] = None
        return jsonify(session_id=session['session_id']), 200

    session['failed_attempts'] += 1
    if session['failed_attempts'] > 3:
        session['lockout_time'] = time.time() + 30
        error = "Too many failed attempts. Please try again in 30 seconds."

    return jsonify({"error": error}), 401

@app.route('/google/login')
def google_login():
    """Redirect user to Google OAuth login page."""
    return google.authorize_redirect(url_for('google_callback', _external=True), prompt="select_account")

@app.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback and store user info in session."""
    token = google.authorize_access_token()
    user_info = google.get("userinfo").json()
    session['google_user'] = user_info

    # Generate a unique session ID if it's not already present
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

    # Send session ID to mobile app
    return jsonify(session_id=session['session_id']), 200

@app.route('/logout')
def logout():
    """Logout and clear session data."""
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/google/token-login', methods=['POST'])
def google_token_login():
    data = request.get_json()
    token = data.get('id_token')

    if not token:
        return jsonify({"error": "Missing ID token"}), 400

    try:
        # Verify token using Google’s public keys
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), 
            "1045716424808-g5ckn3rgeuj0h628f2acbershk2p5vc9.apps.googleusercontent.com")      #web client id #web and android client id's must be in the same project


        # You can now extract user info like:
        user_id = idinfo['sub']
        email = idinfo.get('email')
        name = idinfo.get('name')

        session['google_user'] = {"email": email, "name": name, "sub": user_id}
        session['session_id'] = str(uuid.uuid4())

        return jsonify(session_id=session['session_id']), 200

    except ValueError as e:
        return jsonify({"error": "Invalid ID token"}), 401
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)