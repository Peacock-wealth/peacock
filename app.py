from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from pymongo import MongoClient
from flask_cors import CORS
import os

app = Flask(__name__)

# ------------------- CORS FIX -------------------
CORS(app, resources={r"/*": {"origins": [
    "https://peacockfrontends.onrender.com",
    "https://peacockwealthmanagement.com",
    "https://www.peacockwealthmanagement.com"
]}}, supports_credentials=True)

@app.after_request
def after_request(response):
    origin = request.headers.get("Origin")
    allowed_origins = [
        "https://peacockfrontends.onrender.com",
        "https://peacockwealthmanagement.com",
        "https://www.peacockwealthmanagement.com"
    ]

    if origin in allowed_origins:
        response.headers.add("Access-Control-Allow-Origin", origin)

    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    return response


# ------------------- MongoDB Setup (via environment variable) -------------------
mongo_uri = os.getenv("MONGO_URI")   # <-- DO NOT CHANGE THIS
client = MongoClient(mongo_uri)
db = client["demo_db"]
contacts_collection = db["contacts"]


# ------------------- Email Setup (via environment variables) -------------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")  # <-- DO NOT CHANGE
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")  # <-- DO NOT CHANGE
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

mail = Mail(app)


# ------------------- Routes -------------------
@app.route("/")
def home():
    return "Backend Running Successfully 🚀"


@app.route("/demo/contact", methods=["POST"])
def contact():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    requirements = data.get("requirements")
    message = data.get("message")

    if not all([name, email, message]):
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    # Save into MongoDB
    contacts_collection.insert_one({
        "name": name,
        "email": email,
        "requirements": requirements,
        "message": message
    })
        # Send notification email
    subject_line = f"New Contact Message from {name}".replace("\n", "").strip()

    body_text = (
        "New Contact Form Submission\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Requirements: {requirements}\n"
        f"Message: {message}\n"
    )

    msg = Message(
        subject=subject_line,
        sender=app.config["MAIL_USERNAME"],
        recipients=[app.config["MAIL_USERNAME"]],
    )

    msg.body = body_text
    mail.send(msg)


    return jsonify({"status": "success", "message": "Message sent successfully!"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
