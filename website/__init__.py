'''
This module sets up our Flask application.
'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail

# Initialize database and mail objects
db = SQLAlchemy()
mail = Mail()

# Set the name of the database file
DB_NAME = "database.db"

def create_app():
    '''
    This function creates and configures our Flask application.
    '''
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['SECRET_KEY'] = 'AB-IYuh'  # A better secret key might be needed for real applications
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Import and register blueprints for views and authentication
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import user and admin_user models
    from .models import User, Admin_User

    # Create the database if it doesn't exist
    create_database(app)

    # Configure login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Configure mail settings
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'iyasuasnake4@gmail.com'
    app.config['MAIL_PASSWORD'] = 'snrr hmbn cqpo txts'
    mail = Mail(app)

    @login_manager.user_loader
    def load_user(id):
        # Try to load the user from the User model
        user = User.query.get(id)
        if user:
            return user

        # Try to load the user from the Admin_User model
        admin_user = Admin_User.query.get(id)
        if admin_user:
            return admin_user

        return None

    return app

def create_database(app):
    '''
    This function creates the database if it doesn't exist.
    '''
    if not path.exists('website/instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!')
