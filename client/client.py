"""
Simple Terminal Chat Client.
Connects to Flask-SocketIO chat server.
"""

import socketio
import requests
import sys
import time
import os


class ChatClient:
    """Chat client with simplified interface."""

    def __init__(self, server_url="http://localhost:5050"):
        self.server_url = server_url
        self.username = None
        self.is_connected = False

        # Initialize SocketIO client
        self.sio = socketio.Client(
            reconnection_attempts=3,
            reconnection_delay=1,
            logger=False
        )

        # Setup event handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup SocketIO event handlers."""

        @self.sio.event
        def connect():
            print("[System] Connected to server")
            self.is_connected = True

        @self.sio.event
        def disconnect():
            print("\n[System] Disconnected from server")
            self.is_connected = False

        @self.sio.on('new_message')
        def handle_message(data):
            self._display_message(data)

        @self.sio.on('user_joined')
        def handle_user_joined(data):
            message = data.get('message', '')
            if message:
                print(f"\n[System] {message}")

        @self.sio.on('user_left')
        def handle_user_left(data):
            message = data.get('message', '')
            if message:
                print(f"\n[System] {message}")

        @self.sio.on('message_history')
        def handle_history(data):
            messages = data.get('messages', [])
            if messages:
                print("\n" + "=" * 40)
                print("Chat History")
                print("=" * 40)
                for msg in messages:
                    self._display_message(msg, show_own=True)
                print("=" * 40)

        @self.sio.on('online_users')
        def handle_online_users(data):
            users = data.get('users', [])
            count = len(users)
            if count > 0:
                print(f"\n[System] Online users ({count}): {', '.join(users)}")
            else:
                print("\n[System] You are the only one online")

        @self.sio.on('error')
        def handle_error(data):
            message = data.get('message', 'Unknown error')
            print(f"\n[Error] {message}")

    def _display_message(self, data, show_own=False):
        """Display a message in readable format."""
        timestamp = data.get('timestamp', '')
        username = data.get('username', '')
        content = data.get('content', '')

        # Extract time part if timestamp has date
        if ' ' in timestamp:
            time_part = timestamp.split()[1]
        else:
            time_part = timestamp

        # Don't show our own messages unless show_own is True (for history)
        if username != self.username or show_own:
            if show_own:
                # For history, no leading newline
                print(f"[{time_part}] {username}: {content}")
            else:
                # For real-time messages, add newline to separate from input
                print(f"\n[{time_part}] {username}: {content}")

    def _send_request(self, endpoint, data):
        """Send HTTP request to server."""
        url = f"{self.server_url}{endpoint}"

        try:
            response = requests.post(
                url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )

            # Try to parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {}

            return response.status_code, response_data

        except requests.exceptions.ConnectionError:
            print(f"[Error] Cannot connect to server at {self.server_url}")
            return None, {}
        except requests.exceptions.Timeout:
            print("[Error] Connection timeout")
            return None, {}
        except Exception as e:
            print(f"[Error] Request failed: {e}")
            return None, {}

    def register(self, username, password):
        """Register a new user."""
        status_code, data = self._send_request('/register', {
            'username': username,
            'password': password
        })

        if status_code == 201:
            print("[System] Registration successful")
            return True
        elif status_code == 400:
            # Server returns 'message' key, not 'error'
            error_msg = data.get('message', 'Bad request')
            print(f"[Error] {error_msg}")
            return False
        elif status_code == 409:
            error_msg = data.get('message', 'Username already exists')
            print(f"[Error] {error_msg}")
            return False
        elif data and 'message' in data:
            print(f"[Error] {data['message']}")
            return False
        else:
            print(f"[Error] Registration failed (status: {status_code})")
            return False

    def login(self, username, password):
        """Login user."""
        status_code, data = self._send_request('/login', {
            'username': username,
            'password': password
        })

        if status_code == 200:
            print("[System] Login successful")
            self.username = username
            return True
        elif status_code == 401:
            # Server returns 'message' key, not 'error'
            error_msg = data.get('message', 'Invalid username or password')
            print(f"[Error] {error_msg}")
            return False
        elif status_code == 400:
            error_msg = data.get('message', 'Bad request')
            print(f"[Error] {error_msg}")
            return False
        elif data and 'message' in data:
            print(f"[Error] {data['message']}")
            return False
        else:
            print(f"[Error] Login failed (status: {status_code})")
            return False

    def connect_to_chat(self):
        """Connect to chat server."""
        if not self.username:
            print("[Error] Must login first")
            return False

        try:
            print(f"[System] Connecting to chat as {self.username}...")
            self.sio.connect(self.server_url)

            # Wait for connection
            for _ in range(10):
                if self.is_connected:
                    break
                time.sleep(0.1)

            if not self.is_connected:
                print("[Error] Connection timeout")
                return False

            # Join chat room
            self.sio.emit('join', {'username': self.username})
            time.sleep(0.5)  # Small delay for history loading

            return True

        except Exception as e:
            print(f"[Error] Connection failed: {e}")
            return False

    def send_message(self, content):
        """Send a message to chat."""
        if not self.is_connected:
            print("[Error] Not connected to chat")
            return

        if not content.strip():
            print("[Error] Message cannot be empty")
            return

        # Show our own message (input section already cleared by loop)
        current_time = time.strftime('%H:%M:%S')
        print(f"[{current_time}] You: {content}")

        # Send to server (loop will reshow input section)
        self.sio.emit('send_message', {'content': content})

    def get_online_users(self):
        """Request online users list."""
        if self.is_connected:
            self.sio.emit('get_online_users')

    def disconnect(self):
        """Disconnect from server."""
        if self.is_connected:
            self.sio.disconnect()

    def _check_server(self):
        """Check if server is reachable with retry for Docker startup."""
        max_retries = 5
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                # Try to connect to the server root
                _ = requests.get(self.server_url, timeout=5)
                # Server is reachable if we get any response (even 404)
                print("[System] Server is reachable")
                return True
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    print(f"[System] Waiting for server... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"[Error] Cannot connect to server at {self.server_url}")
                    print("Please make sure:")
                    print("  1. Server is running (run python app.py)")
                    print("  2. URL is correct")
                    print("  3. Port 5050 is not blocked")
                    return False
            except Exception as e:
                print(f"[Error] Server check failed: {e}")
                return False

        return False

    def _show_help(self):
        """Show help menu."""
        print("\n" + "=" * 40)
        print("Available Commands")
        print("=" * 40)
        print("/users    - Show online users")
        print("/exit     - Leave chat")
        print("/help     - Show this help")
        print("=" * 40)

    def run(self):
        """Run the chat client."""
        print("\n" + "=" * 50)
        print("Terminal Chat Client")
        print("=" * 50)
        print(f"Server: {self.server_url}")
        print("=" * 50)

        # Check server
        if not self._check_server():
            return

        # Authentication loop
        while True:
            print("\n1. Register")
            print("2. Login")
            print("3. Exit")

            try:
                choice = input("\nChoose (1-3): ").strip()

                if choice == '3':
                    print("\nGoodbye!")
                    return

                if choice not in ['1', '2']:
                    print("\nPlease choose 1, 2, or 3")
                    continue

                username = input("Username: ").strip()
                password = input("Password: ").strip()

                if not username or not password:
                    print("\nBoth username and password are required")
                    continue

                # Register if needed
                if choice == '1':
                    if not self.register(username, password):
                        retry = input("\nTry again? (y/n): ").lower()
                        if retry != 'y':
                            return
                        continue

                # Login
                if self.login(username, password):
                    break
                else:
                    retry = input("\nTry again? (y/n): ").lower()
                    if retry != 'y':
                        return

            except KeyboardInterrupt:
                print("\n\n[System] Registration cancelled")
                return
            except Exception as e:
                print(f"\n[Error] Input error: {e}")
                return

        # Connect to chat
        if not self.connect_to_chat():
            return

        # Chat loop
        print("\n" + "=" * 50)
        print(f"Welcome to the chat, {self.username}!")
        print("Type /help for commands")
        print("=" * 50)

        try:
            while self.is_connected:
                try:
                    # Show simple prompt
                    print("\n" + "-" * 30)
                    message = input("You: ").strip()

                    if not message:
                        continue

                    # Handle commands
                    if message.lower() == '/exit':
                        print("[System] Leaving chat...")
                        break
                    elif message.lower() == '/users':
                        self.get_online_users()
                    elif message.lower() == '/help':
                        self._show_help()
                    else:
                        self.send_message(message)

                except KeyboardInterrupt:
                    print("\n[System] Interrupted")
                    break
                except EOFError:
                    print("\n[System] Input closed")
                    break

        except Exception as e:
            print(f"\n[Error] {e}")

        finally:
            # Cleanup
            self.disconnect()
            print("\n[System] Disconnected. Goodbye!")


def main():
    """Main entry point."""

    # Check dependencies (bcrypt removed - not needed for client)
    try:
        import socketio
        import requests
    except ImportError as e:
        print(f"\n[Error] Missing required package: {e.name}")
        print("Install with: pip install python-socketio requests")
        return

    # Get server URL from environment variable first, then command line, then default
    import os
    import argparse

    default_url = os.environ.get('SERVER_URL', 'http://localhost:5050')

    parser = argparse.ArgumentParser(description='Terminal Chat Client')
    parser.add_argument('--server', default=default_url,
                       help=f'Server URL (default: {default_url})')

    args = parser.parse_args()

    # Create and run client
    client = ChatClient(args.server)

    try:
        client.run()
    except KeyboardInterrupt:
        print("\n\n[System] Client stopped by user")
    except Exception as e:
        print(f"\n[Error] Fatal error: {e}")


if __name__ == "__main__":
    main()