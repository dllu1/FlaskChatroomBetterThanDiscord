"""
Database configuration and setup module.

This module initializes the SQLAlchemy database instance and provides
a function to create all database tables.
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()


def init_database(app):
    """
    Initialize the database with the Flask application.

    Args:
        app: Flask application instance

    This function configures the database URI and creates all tables
    defined in the models if they don't already exist.
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatroom.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()