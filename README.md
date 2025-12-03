# Chatroom Application

A terminal-based chatroom application built with Flask-SocketIO for real-time messaging.

## Project Structure

```
chatroom/
├── server/
│   ├── app.py              # Flask + SocketIO server
│   ├── models.py           # Database models (User, Message)
│   ├── database.py         # Database configuration
│   ├── requirements.txt    # Server dependencies
│   └── Dockerfile          # Server container configuration
├── client/
│   ├── client.py           # Terminal client application
│   ├── requirements.txt    # Client dependencies
│   └── Dockerfile          # Client container configuration
├── docker-compose.yml      # Container orchestration
└── README.md               # This file
```

## Features

- User registration with unique usernames
- Secure login with hashed passwords (bcrypt)
- Real-time message broadcasting to all connected users
- Message history on join (last 50 messages)
- Online users list
- Persistent message storage in SQLite database
- Graceful logout with Ctrl+C or /exit command
- Dockerized deployment (both server and client)

## Requirements

- Python 3.11+
- Docker and Docker Compose (optional)

## Installation

### Option 1: Running with Docker (Recommended)

1. Build and start both server and client containers:

   ```bash
   docker-compose up --build
   ```

   The server will be available at `http://localhost:5050`

2. To run the client interactively:

   ```bash
   docker-compose run --rm chat-client
   ```

3. To stop all containers:

   ```bash
   docker-compose down
   ```

### Option 2: Running Without Docker

#### Server Setup

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

   Server will start at `http://localhost:5050`

#### Client Setup

1. Open a new terminal and navigate to the client directory:

   ```bash
   cd client
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install client dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the client:

   ```bash
   python client.py
   ```

5. To connect to a different server:

   ```bash
   python client.py --server http://your-server-address:5050
   ```

## Usage

1. Start the server (using Docker or manually)
2. Run the client application
3. Choose to either:
   - **Register (1)**: Create a new account
   - **Login (2)**: Log in with existing credentials
   - **Exit (3)**: Quit the application
4. Once logged in, you can:
   - Type messages and press Enter to send
   - Use `/users` to see online users
   - Use `/help` to see available commands
   - Use `/exit` or press Ctrl+C to logout

### Client Commands

| Command | Description |
|---------|-------------|
| `/users` | Show list of online users |
| `/help` | Show available commands |
| `/exit` | Leave the chat and disconnect |
| `Ctrl+C` | Graceful exit |

## Technologies Used

| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Framework | Flask 3.1.2 | HTTP request handling |
| Real-time Communication | Flask-SocketIO 5.5.1 | WebSocket support |
| Database ORM | Flask-SQLAlchemy 3.1.1 | Database operations |
| Database | SQLite | Data storage |
| Password Hashing | bcrypt 5.0.0 | Secure password storage |
| Async Support | gevent 25.9.1 | Handle multiple connections |
| Client SocketIO | python-socketio 5.15.0 | Client-server communication |
| HTTP Client | requests 2.31.0 | HTTP requests from client |
| Containerization | Docker | Deployment |

## Protocols Used

| Protocol | Used For | Implementation |
|----------|----------|----------------|
| HTTP | Authentication (login/register) | Flask routes with `@app.route()` |
| WebSocket | Real-time messaging | Flask-SocketIO with `@socketio.on()` |

### Why Two Protocols?

- **HTTP**: Simple request-response for one-time operations like login and registration
- **WebSocket**: Persistent bidirectional connection for real-time chat messages

## API Endpoints

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/register` | POST | Create new account | `{"username": "", "password": ""}` | `{"success": true/false, "message": ""}` |
| `/login` | POST | Authenticate user | `{"username": "", "password": ""}` | `{"success": true/false, "message": ""}` |

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful login |
| 201 | Created | Account created |
| 400 | Bad Request | Missing or invalid data |
| 401 | Unauthorized | Invalid credentials |
| 409 | Conflict | Username already exists |
| 500 | Server Error | Database or server error |

## SocketIO Events

| Event | Direction | Description | Data |
|-------|-----------|-------------|------|
| `connect` | Client → Server | Client connects | - |
| `disconnect` | Client → Server | Client disconnects | - |
| `join` | Client → Server | Join chatroom | `{"username": ""}` |
| `send_message` | Client → Server | Send a message | `{"content": ""}` |
| `get_online_users` | Client → Server | Request online users | - |
| `new_message` | Server → Client | Broadcast new message | `{"username": "", "content": "", "timestamp": ""}` |
| `message_history` | Server → Client | Send chat history | `{"messages": [...]}` |
| `user_joined` | Server → Client | User joined notification | `{"username": "", "message": ""}` |
| `user_left` | Server → Client | User left notification | `{"username": "", "message": ""}` |
| `online_users` | Server → Client | List of online users | `{"users": [...]}` |
| `error` | Server → Client | Error message | `{"message": ""}` |

## Database Schema

### Users Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique user ID |
| username | String(50) | Unique, Not Null | User's username |
| password_hash | String(255) | Not Null | Hashed password (bcrypt) |

### Messages Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique message ID |
| username | String(50) | Not Null | Sender's username |
| content | Text | Not Null | Message content |
| timestamp | DateTime | Not Null, Default: UTC now | Time message was sent |

## Error Handling

This application implements comprehensive error handling to ensure graceful operation and clear user feedback.

### Server-Side Error Handling

| Error Type | HTTP Code | Response Message |
|------------|-----------|------------------|
| No data provided | 400 | "No data provided" |
| Empty username/password | 400 | "Username and password are required" |
| Duplicate username | 409 | "Username already exists" |
| Invalid credentials | 401 | "Invalid username or password" |
| Database errors | 500 | "Registration/Login failed: {error}" |
| Not found | 404 | "Not found" |
| Internal error | 500 | "Internal server error" |

### Client-Side Error Handling

| Error Type | How It's Handled |
|------------|------------------|
| Server not running | Displays connection error with troubleshooting tips |
| Connection timeout | Shows timeout error after 5 seconds |
| Network disconnection | Displays "[System] Disconnected from server" |
| Empty message | Prevents sending with error message |
| Invalid input | Shows appropriate error and prompts retry |
| Keyboard interrupt | Graceful disconnect and cleanup |

### Graceful Exit

When the user presses `Ctrl+C` or types `/exit`, the application:

1. Catches the interrupt signal or command
2. Prints disconnect message
3. Disconnects from the SocketIO server properly
4. Server notifies other users that this user has left
5. Exits cleanly without crashing

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

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Cannot connect to server" | Server not running | Start server with `python app.py` |
| "Username already exists" | Duplicate registration | Choose a different username |
| "Invalid username or password" | Wrong credentials | Check spelling and try again |
| "You must join the chat first" | Sending without joining | Login before sending messages |
| "Message cannot be empty" | Blank message | Type a message before sending |
| Connection refused | Wrong port or firewall | Check server is running on port 5050 |

## Best Practices Followed

| Practice | Implementation |
|----------|----------------|
| DRY (Don't Repeat Yourself) | Reusable `_send_request()` method in client, shared `to_dict()` methods in models |
| SRP (Single Responsibility) | Separate files: `models.py` for data, `database.py` for DB config, `app.py` for routes |
| SSOT (Single Source of Truth) | Database as the only source for user and message data |
| PEP8 | Code follows Python style guidelines with docstrings |
| Input Validation | All user inputs validated before processing |
| Secure Passwords | Passwords hashed using bcrypt, never stored as plain text |
| Error Handling | Try-except blocks with rollback, user-friendly error messages |
| Graceful Shutdown | Signal handlers for clean disconnection |

## Docker Configuration

### docker-compose.yml Services

| Service | Container Name | Port | Description |
|---------|---------------|------|-------------|
| chat-server | chat-server | 5050:5050 | Flask-SocketIO server |
| chat-client | chat-client | - | Interactive terminal client |

### Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Run client interactively
docker-compose run --rm chat-client

# Stop all services
docker-compose down

# Remove volumes (clears database)
docker-compose down -v
```

### Environment Variables

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| FLASK_ENV | chat-server | production | Flask environment |
| SERVER_URL | chat-client | http://chat-server:5050 | Server URL for client |

## Troubleshooting

### Server Issues

| Problem | Solution |
|---------|----------|
| Port already in use | Kill existing process or change port in `app.py` |
| Database locked | Restart server, ensure only one instance running |
| Module not found | Run `pip install -r requirements.txt` |

### Client Issues

| Problem | Solution |
|---------|----------|
| Cannot connect | Ensure server is running first |
| Connection refused | Check SERVER_URL matches server address |
| Messages not appearing | Check network connection |

### Docker Issues

| Problem | Solution |
|---------|----------|
| Container won't start | Check logs with `docker-compose logs` |
| Network issues | Ensure containers are on same network |
| Permission denied | Run with `sudo` or fix Docker permissions |

## Authors

[Dat Luan Lu, Maxim Orechnikov]