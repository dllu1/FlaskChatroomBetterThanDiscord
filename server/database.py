"""
Database python management
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Initialize SQLAlchemy instance - Single Source of Truth
db = SQLAlchemy()


def init_database(app):
    """
    Initialize database with Flask application.

    Args:
        app: Flask application instance
    """
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatroom.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database with app
    db.init_app(app)

    # Create all tables
    with app.app_context():
        db.create_all()


def check_database_connection():
    """
    Check if database connection is working.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        db.session.execute(text('SELECT 1'))
        return True
    except Exception:
        return False