# app.py
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from pymongo import MongoClient
from flask_cors import CORS
from urllib.parse import quote_plus

app = Flask(__name__)
CORS(app)  # Frontend (Live Server) can talk to backend

# ------------------- MongoDB setup -------------------
# Replace with your MongoDB user credentials
# ------------------- MongoDB setup -------------------
username = quote_plus("peacockwealthmanagement_db_user")  
password = quote_plus("peacockcompanys")                  
database_name = "demo_db"

mongo_uri = f"mongodb+srv://peacockwealthmanagement_db_user:peacockcompanys@cluster0.63qkmrg.mongodb.net/demo_db?retryWrites=true&w=majority"

client = MongoClient(mongo_uri)
db = client['demo_db']
contacts_collection = db["contacts"]

# ------------------- Email setup -------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'contact@peacock.org.in'
app.config['MAIL_PASSWORD'] = 'tcna uwdb jxzh ygsb'  # Gmail app password recommended
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# ------------------- Routes -------------------
@app.route('/')
def home():
    return "Flask backend running successfully!"

@app.route('/demo/contact', methods=['POST'])
def contact():
    data = request.json
    
    print("Form data received →", data) 
    
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

    # Send email
    msg = Message(
        subject=f"New Contact Message from {name}",
        sender=app.config['MAIL_USERNAME'],
        recipients=[app.config['MAIL_USERNAME']]
    )
    msg.body = f"Name: {name}\nEmail:fRequirements: {requirements}\n {email}\nMessage: {message}"
    mail.send(msg)

    return jsonify({"status": "success", "message": "Message sent successfully!"}),200

# ------------------- Run Flask -------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)  # use_reloader=False avoids WinError 10038
