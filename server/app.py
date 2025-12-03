"""
Flask SocketIO Chat Server.
Handles user authentication and real-time messaging.
"""

import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import bcrypt

from database import db, init_database, check_database_connection
from models import User, Message

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chat_secret_key_123'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database
init_database(app)

# Store connected users
connected_users = {}  # {session_id: username}


def validate_json_request(required_fields):
    """
    Validate JSON request data (DRY principle).

    Args:
        required_fields: List of required field names

    Returns:
        tuple: (data, error_response, status_code)
    """
    try:
        data = request.get_json()
        if not data:
            return None, {'error': 'No data provided'}, 400

        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return None, {'error': f'Missing or empty field: {field}'}, 400

        return data, None, None

    except Exception as e:
        logger.error(f"Request validation failed: {e}")
        return None, {'error': 'Invalid JSON data'}, 400


# ==================== HTTP Routes ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        if check_database_connection():
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'online_users': len(connected_users)
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected'
            }), 500
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'error': 'Health check failed'}), 500


@app.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data, error_response, status_code = validate_json_request(['username', 'password'])
    if error_response:
        return jsonify(error_response), status_code

    username = data['username'].strip()
    password = data['password']

    try:
        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409

        # Create user (no restrictions)
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"User registered: {username}")
        return jsonify({'message': 'Registration successful'}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/login', methods=['POST'])
def login():
    """Login user."""
    data, error_response, status_code = validate_json_request(['username', 'password'])
    if error_response:
        return jsonify(error_response), status_code

    username = data['username'].strip()
    password = data['password']

    try:
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401

        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid username or password'}), 401

        logger.info(f"User logged in: {username}")
        return jsonify({
            'message': 'Login successful',
            'username': username
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500


# ==================== SocketIO Handlers ====================

@socketio.on('connect')
def handle_connect():
    """Handle new client connection."""
    session_id = request.sid
    logger.info(f"Client connected: {session_id}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    session_id = request.sid

    if session_id in connected_users:
        username = connected_users[session_id]
        del connected_users[session_id]

        # Notify all users
        emit('user_left', {
            'username': username,
            'message': f'{username} left the chat'
        }, broadcast=True)

        logger.info(f"User disconnected: {username}")


@socketio.on('join')
def handle_join(data):
    """Handle user joining chat."""
    session_id = request.sid
    username = data.get('username', '').strip()

    if not username:
        emit('error', {'message': 'Username is required'})
        return

    # Store user
    connected_users[session_id] = username

    try:
        # Send recent messages
        recent_messages = Message.query.order_by(Message.timestamp.asc()).limit(50).all()
        messages_data = [msg.to_dict() for msg in recent_messages]
        emit('message_history', {'messages': messages_data})

        # Notify all users
        emit('user_joined', {
            'username': username,
            'message': f'{username} joined the chat'
        }, broadcast=True)

        logger.info(f"User joined: {username}")

    except Exception as e:
        logger.error(f"Failed to load messages: {e}")
        emit('error', {'message': 'Failed to load chat history'})


@socketio.on('send_message')
def handle_send_message(data):
    """Handle incoming message."""
    session_id = request.sid

    # Check if user is connected
    if session_id not in connected_users:
        emit('error', {'message': 'Please join the chat first'})
        return

    username = connected_users[session_id]
    content = data.get('content', '').strip()

    if not content:
        emit('error', {'message': 'Message cannot be empty'})
        return

    try:
        # Save message
        new_message = Message(username=username, content=content)
        db.session.add(new_message)
        db.session.commit()

        # Broadcast message
        emit('new_message', new_message.to_dict(), broadcast=True)

        logger.info(f"Message from {username}: {content[:50]}")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to save message: {e}")
        emit('error', {'message': 'Failed to send message'})


@socketio.on('get_online_users')
def handle_online_users():
    """Send list of online users."""
    try:
        users = list(set(connected_users.values()))
        emit('online_users', {'users': users})
    except Exception as e:
        logger.error(f"Failed to get online users: {e}")
        emit('error', {'message': 'Failed to get online users'})


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ==================== Main Entry Point ====================

if __name__ == '__main__':
    print("=" * 50)
    print("Chat Server Starting")
    print("=" * 50)
    print("Server URL: http://localhost:5050")
    print("Health check: http://localhost:5050/health")
    print("=" * 50)

    try:
        socketio.run(app, host='0.0.0.0', port=5050, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"Error: {e}")