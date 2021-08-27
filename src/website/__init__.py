from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_cors import CORS
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
DB_NAME = "delivery_app.db"
ma = Marshmallow()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretsecretsecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    ma.init_app(app)
    CORS(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')

    from .models import User, Delivery
    create_database(app)

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database')
