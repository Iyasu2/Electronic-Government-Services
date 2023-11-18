'''
this module sets up our flask application
'''
from flask import Flask

def create_app():
    '''
    this will create and configure our flask application
    '''
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'AB-IYuh' #a better secret key might be needed for real applications

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    return app