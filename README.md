# Chatroom Application

A terminal-based chatroom application built with Flask-SocketIO for real-time messaging.

## Project Structure

```
chatroom/
├── server/
│   ├── app.py              # Flask + SocketIO server
│   ├── models.py           # Database models (User, Message)
│   ├── database.py         # Database configuration
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Server container configuration
├── client/
│   └── client.py           # Terminal client application
├── docker-compose.yml      # Container orchestration
└── README.md               # This file
```

## Features

- User registration with unique usernames
- Secure login with hashed passwords
- Real-time message broadcasting to all connected users
- Persistent message storage in SQLite database
- Graceful logout with Ctrl+C
- Dockerized server deployment

## Requirements

- Python 3.11+
- Docker and Docker Compose

## Installation

### Server Setup (Docker)

1. Build and start the server container:

   ```bash
   docker-compose up --build
   ```

   The server will be available at `http://localhost:5000`

2. To stop the server:

   ```bash
   docker-compose down
   ```

### Server Setup (Without Docker)

1. Navigate to the server directory:

   ```bash
   cd server
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:

   ```bash
   python app.py
   ```

### Client Setup

1. Navigate to the client directory:

   ```bash
   cd client
   ```

2. Install client dependencies:

   ```bash
   pip install python-socketio[client] requests
   ```

3. Run the client:

   ```bash
   python client.py
   ```

## Usage

1. Start the server using Docker or manually
2. Run the client application
3. Choose to either:
   - Create a new account (register)
   - Log in with existing credentials
4. Once logged in, type messages and press Enter to send
5. Messages from other users appear in real-time
6. Press Ctrl+C to logout and exit

## Technologies Used

- **Flask**: Web framework
- **Flask-SocketIO**: Real-time WebSocket communication
- **Flask-SQLAlchemy**: Database ORM
- **SQLite**: Database storage
- **bcrypt**: Password hashing
- **Docker**: Containerization
- **python-socketio**: Client-side SocketIO library

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | POST | Create new user account |
| `/login` | POST | Authenticate user |

## SocketIO Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `send_message` | Client → Server | Send a chat message |
| `new_message` | Server → Client | Broadcast message to all users |
| `user_joined` | Server → Client | Notify when user connects |
| `user_left` | Server → Client | Notify when user disconnects |

## Database Schema

### Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| username | String(50) | Unique username |
| password_hash | String(255) | Hashed password |

### Messages Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| username | String(50) | Sender username |
| content | Text | Message content |
| timestamp | DateTime | Time message was sent |

## Error Handling

This application implements comprehensive error handling to ensure graceful operation and clear user feedback.

### Server-Side Error Handling

| Error Type | How It's Handled |
|------------|------------------|
| Invalid JSON data | Returns 400 status with "No data provided" message |
| Empty username/password | Returns 400 status with "Username and password are required" |
| Duplicate username | Returns 409 status with "Username already exists" |
| Invalid credentials | Returns 401 status with "Invalid username or password" |
| Database errors | Rolls back transaction and returns 500 status with error details |
| 404 Not Found | Returns JSON error instead of HTML page |
| 500 Internal Error | Rolls back database and returns JSON error |

### Client-Side Error Handling

| Error Type | How It's Handled |
|------------|------------------|
| Server not running | Displays "Cannot connect to server. Is it running?" |
| Connection timeout | Shows timeout error after 10 seconds |
| Network disconnection | Displays "[Disconnected from server]" |
| Empty message | Prevents sending and prompts for input |
| SocketIO errors | Displays error message from server |

### Graceful Exit (Ctrl+C)

When the user presses `Ctrl+C`, the application:

1. Catches the interrupt signal
2. Sets the running flag to False
3. Disconnects from the SocketIO server properly
4. Notifies other users that this user has left
5. Exits cleanly without crashing

```python
# Signal handler for graceful exit
def graceful_exit(signum, frame):
    global is_running
    is_running = False
    print("\n\nDisconnecting...")
    if sio.connected:
        sio.disconnect()
    print("Goodbye!")
    sys.exit(0)
```

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Cannot connect to server" | Server not running | Start server with `python app.py` |
| "Username already exists" | Duplicate registration | Choose a different username |
| "Invalid username or password" | Wrong credentials | Check spelling and try again |
| "You must join the chat first" | Sending without joining | Login before sending messages |
| "Message cannot be empty" | Blank message | Type a message before sending |
| Connection refused | Wrong port or firewall | Check SERVER_URL in client.py |

### Database Error Recovery

The server uses SQLAlchemy's session management to handle database errors:

```python
try:
    db.session.add(new_user)
    db.session.commit()
except Exception as e:
    db.session.rollback()  # Undo partial changes
    return jsonify({'success': False, 'message': f'Error: {str(e)}'})
```

This ensures the database remains consistent even when errors occur.

## Best Practices Followed

| Practice | Implementation |
|----------|----------------|
| DRY (Don't Repeat Yourself) | Reusable functions for database operations |
| SRP (Single Responsibility) | Separate files for models, database, and routes |
| SSOT (Single Source of Truth) | Database as the only source for user and message data |
| PEP8 | Code follows Python style guidelines |
| Input Validation | All user inputs are validated before processing |
| Secure Passwords | Passwords are hashed using bcrypt, never stored as plain text |

## Authors

[Dat Luan Lu, Maxim Orechnikov]
