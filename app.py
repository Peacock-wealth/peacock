from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from pymongo import MongoClient
from flask_cors import CORS
from urllib.parse import quote_plus
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
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Origin', 'https://peacockwealthmanagement.com')
    return response


# ------------------- MongoDB Setup ✔ CHANGE ADDED -------------------
mongo_uri = os.getenv("mongodb+srv://peacockwealthmanagement_db_user:peacockcompanys@cluster0.63qkmrg.mongodb.net/?appName=Cluster0 ")  # <-- YOU MUST ADD THIS

client = MongoClient(mongo_uri)
db = client["demo_db"]
contacts_collection = db["contacts"]

# ------------------- Email Setup ✔ CHANGE ADDED -------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv("contact@pacock.org.in")  # <-- YOU MUST ADD THIS
app.config['MAIL_PASSWORD'] = os.getenv("tcna uwdb jxzh ygsb")  # <-- YOU MUST ADD THIS
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# ------------------- Routes -------------------
@app.route('/')
def home():
    return "Backend Running Successfully 🚀"

@app.route('/demo/contact', methods=['POST'])
def contact():
    data = request.json

    name = data.get('name')
    email = data.get('email')
    requirements = data.get('requirements')
    message = data.get('message')

    if not all([name, email, message]):
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    # Save to MongoDB
    contacts_collection.insert_one({
        "name": name,
        "email": email,
        "requirements": requirements,
        "message": message
    })

    # Send email notification
    msg = Message(
        subject=f"New Contact Message from {name}",
        sender=app.config['MAIL_USERNAME'],
        recipients=[app.config['MAIL_USERNAME']]
    )
    msg.body = f"""
Name: {name}
Email: {email}
Requirements: {requirements}
Message: {message}
"""
    mail.send(msg)

    return jsonify({"status": "success", "message": "Message sent successfully!"}), 200


# ------------------- Gunicorn entrypoint ✔ CHANGE ADDED -------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
