from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, send, emit
import json
import os
import random
import string

# Initialize Flask app and Flask-SocketIO
app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)

# Load user data from the JSON file
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

# Save user data to the JSON file
def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

# Load existing messages from JSON file
def load_messages():
    if os.path.exists("messages.json"):
        with open("messages.json", "r") as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open("messages.json", "w") as f:
        json.dump(messages, f)

@app.route("/")
def home():
    return redirect(url_for('index.html'))

@app.route("/index.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and users[username]["password"] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 400
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username not in users:
            user_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            users[username] = {"user_id": user_id, "password": password}
            save_users(users)
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Username already exists", 400
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("dashboard.html")

# SocketIO events for real-time messaging
@socketio.on('send_message')
def handle_send_message(data):
    message = data["message"]
    username = session.get('user', '')
    timestamp = data["timestamp"]
    new_message = {
        "sender": username,
        "message": message,
        "timestamp": timestamp
    }
    messages = load_messages()
    messages.append(new_message)
    save_messages(messages)
    emit('receive_message', new_message, broadcast=True)

# Serve chat page
@app.route("/chat")
def chat():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("chat.html")

# Handle sending messages via POST request (for REST API)
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()

    # Extract data from the request
    message = data.get('message')
    timestamp = data.get('timestamp')
    username = data.get('username')

    if not message or not username:
        return jsonify({'status': 'error', 'message': 'Message and username are required'}), 400

    # Save the message to a JSON file
    new_message = {
        'sender': username,
        'message': message,
        'timestamp': timestamp
    }

    # Append to messages.json (this part is simplified)
    try:
        with open('messages.json', 'r+') as f:
            messages = json.load(f)
            messages.append(new_message)
            f.seek(0)
            json.dump(messages, f)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error saving message: {str(e)}'}), 500

    # Return success status with the message
    return jsonify({'status': 'success', 'message': message, 'timestamp': timestamp})

# Running the app
if __name__ == "__main__":
    socketio.run(app, debug=True)

@socketio.on('send_message')
def handle_send_message(data):
    message = data["message"]
    username = data["username"]
    timestamp = data["timestamp"]
    
    new_message = {
        "sender": username,
        "message": message,
        "timestamp": timestamp
    }

    # Optionally save the message to a JSON file
    messages = load_messages()
    messages.append(new_message)
    save_messages(messages)
    
    # Broadcast the message to all connected clients
    emit('receive_message', new_message, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
