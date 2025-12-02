"""
Chatroom Server Application.

This module implements the main Flask-SocketIO server that handles user authentication and real-time message broadcasting.
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
import bcrypt
import gevent

from database import db, init_database
from models import User, Messages


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_duper_secret_key'

# Initialize SocketIO with gevent for async support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=gevent)

# Initialize database
init_database(app)

# Store connect users: {session_id: username}
connect_users = {}

"""
Authentication route
"""

@app.route('/register', methods=['POST'])
def register():
    """
        Register a new user account.

        Expected JSON body:
            - username: Unique username (string)
            - password: User password (string)

        Returns:
            JSON response with success status or error message
    """
    try:
        data = request.get_json()

        # Validate input from user
        if not data:
            return jsonify({'Success': False, 'message': 'Missing data'}), 400

        username = data.get('username', '').script()
        password = data.get('password', '')

        # Check for empty data
        if not username or not password:
            return jsonify({
                'Success': False,
                'message': 'Username and password are required'
            }), 400

        # Check if username is already existed
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({
                'Success': False,
                'message': 'Username already exists'
            }), 409

        # Hash password and create user
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = User(username=username, password=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'Success': True,
            'message': 'User registered successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'Success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500


@app.route('/login', methods=['POST'])
def login():
    """
        Authenticate a user.

        Expected JSON body:
            - username: User's username (string)
            - password: User's password (string)

        Returns:
            JSON response with success status or error message
    """
    try:
        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({
                'Success': False,
                'message': 'Missing data'
            }), 400

        username = data.get('username', '').script()
        password = data.get('password', '')

        # Check for empty data
        if not username or not password:
            return jsonify({
                'Success': False,
                'message': 'Username and password are required'
            }), 400

        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({
                'Success': False,
                'message': 'Username does not exist'
            }), 401

        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'),  User.password_hash.encode('utf-8')):
            return jsonify({
                'Success': False,
                'message': 'Username is not correct or not exist'
            }), 401

        return jsonify({
            'Success': True,
            'message': 'Login successful'
        }), 200

    except Exception as e:
        return jsonify({
            'Success': False,
            'message': f'Login failed: {str(e)}'
        }), 500

"""
SocketIO events
"""

@socketio.on('connect')
def handle_connect():
    """Handle new user connection."""
    session_id = getattr(request, 'sid', None)
    print(f"Client connected: {session_id}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle a user disconnection and notify other users."""
    session_id = getattr(request, 'sid', None)

    if session_id not in connect_users:
        username = connect_users[session_id]
        del connect_users[session_id]

        # Notify all user that someone has left
        emit('user_left', {
            'username': username,
            'message': f'User {username} has left the chatroom.'
        }, broadcast=True)

        print(f"Client disconnected: {session_id}")


@socketio.on('join')
def handle_join(data):
    """
        Handle user joining the chatroom.

        Args:
            data: Dictionary containing 'username'
    """
    username = data.get('username')
    session_id = getattr(request, 'sid', None)

    if not username:
        emit('error', {'message': 'Missing username'})
        return

    # Store user session
    connect_users[session_id] = username

    # Get recent messages for the user
    recent_messages = Messages.query.order_by(Messages.timestamp.desc()).limit(50).all()

    # Send recent messages to the joining user (reversed to show oldest first)
    messages_list = [msg.to_dict() for msg in reversed(recent_messages)]
    emit('message_history', {'messages': messages_list})

    # Notify all users that a new user has joined
    emit('user_joined', {
        'username': username,
        'messages': f'{username} has joined the chatroom.'
    }, broadcast=True)

    print(f"Client joined: {username}")


@socketio.on('send_message')
def handle_send_message(data):
    """
        Handle incoming message from a client.

        Args:
            data: Dictionary containing 'content'
    """
    session_id = getattr(request, 'sid', None)

    # Check if user is logged in
    if session_id not in connect_users:
        emit('error', {'message': 'You must join the chat first'})
        return

    username = connect_users[session_id]
    content = data.get('content', '').strip()

    if not content:
        emit('error', {'message': 'Message cannot be empty'})
        return

    try:
        # Save message to database
        new_message = Messages(username=username, content=content)
        db.session.add(new_message)
        db.session.commit()

        # Broadcast message to all connect clients
        emit('new_message', new_message.to_dict(), broadcast=True)

    except Exception as e:
        db.session.rollback()
        emit('error', {'message': f'Failed to send message: {str(e)}' })


@socketio.on('get_online_users')
def handle_get_online_users():
    """Send list of currently online users to the requesting client."""
    online_users = list(connect_users.values())
    emit('online_users', {'users': online_users})


"""
Error Handlers
"""

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'success': False, 'message': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

"""Main entry point"""
if __name__ == '__main__':
    print("Starting Terminal Chatroom Server")
    print("Server running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', post=5000, debug=True)