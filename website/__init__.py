'''
this module sets up our flask application
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail
from flask_basicauth import BasicAuth
import os
import sqlite3

db =  SQLAlchemy()
mail = Mail()
DB_NAME = "database.db"

def create_app():
    '''
    this will create and configure our flask application
    '''
    app = Flask(__name__)
    app.config['BASIC_AUTH_USERNAME'] = os.environ.get('TWILIO_ACCOUNT_SID')
    app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('TWILIO_AUTH_TOKEN')
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['SECRET_KEY'] = 'AB-IYuh' #a better secret key might be needed for real applications
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User, Admin_User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'iyasuasnake4@gmail.com'
    app.config['MAIL_PASSWORD'] = 'snrr hmbn cqpo txts'

    mail = Mail(app)

    @login_manager.user_loader
    def load_user(id):
        user = User.query.get(id)
        if user:
            return user
        
        admin_user = Admin_User.query.get(id)
        if admin_user:
            return admin_user
        
        return None

    return app

def create_database(app):
    if not path.exists('website/instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!')
