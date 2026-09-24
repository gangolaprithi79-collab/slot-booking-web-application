import os

from flask import Flask
from flask_login import LoginManager

from config import Config

from models import db
from models.user import User
from models.service import Service

from routes import (
    auth_bp,
    booking_bp,
    admin_bp
)


# ==========================================================
# FLASK LOGIN
# ==========================================================

login_manager = LoginManager()

login_manager.login_view = "auth.login"

login_manager.login_message = "Please login to continue."

login_manager.login_message_category = "warning"


# ==========================================================
# CREATE FLASK APPLICATION
# ==========================================================

def create_app():

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)

    # ======================================================
    # REGISTER BLUEPRINTS
    # ======================================================

    app.register_blueprint(auth_bp)

    app.register_blueprint(booking_bp)

    app.register_blueprint(admin_bp)


    # ======================================================
    # CREATE DATABASE TABLES
    # ======================================================

    with app.app_context():

        db.create_all()

        create_default_data()


    return app


# ==========================================================
# LOAD USER FOR FLASK-LOGIN
# ==========================================================

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# ==========================================================
# CREATE DEFAULT ADMIN AND SERVICES
# ==========================================================

def create_default_data():

    # ------------------------------------------------------
    # Admin credentials from .env
    # ------------------------------------------------------

    admin_email = os.getenv(
        "ADMIN_EMAIL",
        "admin@example.com"
    )

    admin_password = os.getenv(
        "ADMIN_PASSWORD",
        "Admin@123"
    )


    # ------------------------------------------------------
    # Check whether admin already exists
    # ------------------------------------------------------

    admin = User.query.filter_by(
        email=admin_email
    ).first()


    # ------------------------------------------------------
    # Create admin if it doesn't exist
    # ------------------------------------------------------

    if not admin:

        admin = User(
            name="Administrator",
            email=admin_email,
            role="admin"
        )

        admin.set_password(
            admin_password
        )

        db.session.add(admin)


    # ------------------------------------------------------
    # Create default services
    # ------------------------------------------------------

    if Service.query.count() == 0:

        services = [

            Service(
                name="Python Consultation",
                duration=30,
                description="Python development consultation"
            ),

            Service(
                name="Technical Interview",
                duration=45,
                description="Technical interview booking"
            ),

            Service(
                name="Project Discussion",
                duration=30,
                description="Project discussion session"
            )

        ]

        db.session.add_all(
            services
        )


    # ------------------------------------------------------
    # Save changes
    # ------------------------------------------------------

    db.session.commit()


# ==========================================================
# CREATE APPLICATION
# ==========================================================

app = create_app()


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )