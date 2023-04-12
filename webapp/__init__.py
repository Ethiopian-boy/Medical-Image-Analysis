from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()

UPLOAD_FOLDER = 'static/uploads/'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']  = 'medical image analysis'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://intellify:password@localhost/analysis'#mysql://username:password@server/db
    db.init_app(app)
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix=('/'))
    app.register_blueprint(auth, url_prefix=('/'))
    
    from .models import User, Note
    
    create_database(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app


def create_database(app):
    with app.app_context():
        db.create_all()
        print("Database created! ")
