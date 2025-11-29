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

## Authors

[Your names here]