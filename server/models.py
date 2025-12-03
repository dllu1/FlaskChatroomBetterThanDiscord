"""
Database models for the chatroom application.

This module defines the User and Message models used to store
user credentials and chat messages in the database.
"""

from datetime import datetime
from database import db


class User(db.Model):
    """
    User model for storing user credentials.

    Attributes:
        id: Unique identifier for the user
        username: Unique username for authentication
        password_hash: Hashed password (never store plain text)
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        """Return string representation of User."""
        return f'<User {self.username}>'

    def to_dict(self):
        """
        Convert user object to dictionary.

        Returns:
            dict: User data without password hash
        """
        return {
            'id': self.id,
            'username': self.username
        }


class Message(db.Model):
    """
    Message model for storing chat messages.

    Attributes:
        id: Unique identifier for the message
        username: Username of the sender
        content: The message text content
        timestamp: Date and time when message was sent
    """

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        """Return string representation of Message."""
        return f'<Message {self.id} from {self.username}>'

    def to_dict(self):
        """
        Convert message object to dictionary.

        Returns:
            dict: Message data in serializable format
        """
        return {
            'id': self.id,
            'username': self.username,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }