#!/usr/bin/env python3
"""
AI‑Survey mailer API
--------------------
POST JSON to /survey/send and the data is e‑mailed to your own Gmail inbox.

Required env variables (can live in a .env file):
    MAIL_USERNAME      your Gmail address
    MAIL_APP_PASSWORD  16‑char App‑Password created in Google › Security › App passwords
"""

import os
from smtplib import SMTPException

from flask import Flask, request, jsonify
from flask_mail import Mail, Message


app = Flask(__name__)
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME="test.hesap458@gmail.com",
    MAIL_PASSWORD="urvl eguj tbja vbqa",
)

mail = Mail(app)


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
            "Cons Per Model:",
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