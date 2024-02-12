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
import psycopg2

db =  SQLAlchemy()
mail = Mail()

def create_app():
    '''
    this will create and configure our flask application
    '''
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    db_url = os.environ.get('POSTGRES_URL')
    db_url_modified = db_url.replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url_modified
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User, Admin_User

    with app.app_context():
        db.drop_all()

    with app.app_context():
        db.create_all()
        print('Created Database!')

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
