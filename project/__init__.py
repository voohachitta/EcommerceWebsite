from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "D:\\Fall 2023-sem1\\Survey of SE\\survey\\instance\\database1.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjahkjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .admin import admin_bp
    from .auth import auth
    from .user import app_bp

    app.register_blueprint(admin_bp, url_prefix='/admin/')
    app.register_blueprint(app_bp, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')

    from .models.app_models import User, Admin, Ratings, Card, Department, Category, Item, Payment, Orders

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Admin.query.get(int(id)) if(session['type'] == 'admin') else User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('project/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')