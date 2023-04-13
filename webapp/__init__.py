from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import mysql.connector


db = SQLAlchemy()

UPLOAD_FOLDER = 'static/uploads/'
cnx = mysql.connector.connect(user='admin', database='ecom', password='Elviskhorem12!?', host='127.0.0.1')
cursor = cnx.cursor(buffered=True)
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'medical image analysis'

    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix=('/'))
    app.register_blueprint(auth, url_prefix=('/'))
    
    from .models import User, Note

    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return
    
    return app



