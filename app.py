import os, re, time, uuid
from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_APP_PASSWORD"),
)

mail = Mail(app)

users = {
    "admin@gmail.com": "password123",
    "admin2@gmail.com": "password123",
    "+1234567890": "password123",
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
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
)

def is_valid_email(v): return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", v)
def is_valid_phone(v): return re.match(r"^\+?\d{10,15}$", v)

@app.route("/session_data")
def session_data():
    if "user" in session: return jsonify({"user": session["user"]}), 200
    if "google_user" in session: return jsonify({"user": session["google_user"]["email"]}), 200
    return jsonify({"error": "No user logged in"}), 401

@app.route("/")
def home():
    if "user" in session: return render_template("home.html", user=session["user"])
    if "google_user" in session: return render_template("home.html", user=session["google_user"]["name"])
    return redirect(url_for("login_page"))

@app.route("/login", methods=["POST"])
def login_page():
    if "session_id" not in session: session["session_id"] = str(uuid.uuid4())
    if "failed_attempts" not in session: session["failed_attempts"] = 0
    if "lockout_time" not in session: session["lockout_time"] = None

    if session["lockout_time"] and time.time() < session["lockout_time"]:
        remaining = int(session["lockout_time"] - time.time())
        return jsonify({"error": f"Too many failed attempts. Try again in {remaining} seconds."}), 401

    data = request.get_json()
    user_input = data.get("user_input", "").strip()
    password = data.get("password", "")

    error = None
    if not user_input or not password: error = "Email/Phone and Password are required."
    elif not (is_valid_email(user_input) or is_valid_phone(user_input)): error = "Invalid email or phone number format."
    elif user_input not in users or users[user_input] != password: error = "Invalid credentials."

    if error:
        session["failed_attempts"] += 1
        if session["failed_attempts"] > 3:
            session["lockout_time"] = time.time() + 30
            error = "Too many failed attempts. Please try again in 30 seconds."
        return jsonify({"error": error}), 401

    session["user"] = user_input
    session["failed_attempts"] = 0
    session["lockout_time"] = None
    return jsonify(session_id=session["session_id"]), 200

@app.route("/google/login")
def google_login(): return google.authorize_redirect(url_for("google_callback", _external=True), prompt="select_account")

@app.route("/google/callback")
def google_callback():
    google.authorize_access_token()
    user_info = google.get("userinfo").json()
    session["google_user"] = user_info
    if "session_id" not in session: session["session_id"] = str(uuid.uuid4())
    return jsonify(session_id=session["session_id"]), 200

@app.route("/google/token-login", methods=["POST"])
def google_token_login():
    token = request.get_json().get("id_token")
    if not token: return jsonify({"error": "Missing ID token"}), 400
    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), "1045716424808-g5ckn3rgeuj0h628f2acbershk2p5vc9.apps.googleusercontent.com")
        session["google_user"] = {"email": idinfo.get("email"), "name": idinfo.get("name"), "sub": idinfo["sub"]}
        session["session_id"] = str(uuid.uuid4())
        return jsonify(session_id=session["session_id"]), 200
    except ValueError:
        return jsonify({"error": "Invalid ID token"}), 401

@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/survey/send", methods=["POST"])
def send_survey():
    data = request.get_json(force=True)

    model_cons = data.get("model_cons", {})
    cons_section = "\n".join([f"{model}: {reason}" for model, reason in model_cons.items()])

    body = "\n".join(
        [
            f"Name: {data.get('name', '')}",
            f"Birth Date: {data.get('birth_date', '')}",
            f"Education Level: {data.get('education_level', '')}",
            f"City: {data.get('city', '')}",
            f"Gender: {data.get('gender', '')}",
            f"Models Tried: {', '.join(data.get('models_tried', []))}",
            "Defects/Cons Per Model:",
            cons_section,
            f"Use Case: {data.get('use_case', '')}",
        ]
    )

    msg = Message(
        subject="AI‑Survey Result",
        sender="test.hesap458@gmail.com",
        recipients=["test.hesap458@gmail.com"],
        body=body,
    )

    try:
        mail.send(msg)
        return jsonify(success=True, message="Mail sent"), 200
    except SMTPException as exc:
        return jsonify(success=False, message=f"Mail error: {exc}"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
