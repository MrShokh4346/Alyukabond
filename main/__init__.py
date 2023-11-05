from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from sqlalchemy import MetaData
from dotenv.main import load_dotenv
import os
from flask_jwt_extended import JWTManager
from datetime import timedelta


load_dotenv()


naming_convention = {
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config["SECRET_KEY"] = os.environ['SECRET_KEY']


    db.init_app(app=app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # from silk_road.auth import bp as auth_bp
    # app.register_blueprint(auth_bp, url_prefix="/auth/v1")

    # from silk_road.api import bp as api_bp
    # app.register_blueprint(api_bp, url_prefix="/api/v1")

    # from silk_road.payment import bp as payment_bp
    # app.register_blueprint(payment_bp, url_prefix="/payment/v1")

    # from silk_road.models import Category
    # @app.cli.command('add-category')
    # def add_category():
    #     name = input("name: ")
    #     icon = input("icon: ")
    #     category = Category(name=name, icon=icon)
    #     with app.app_context():
    #         db.session.add(category)
    #         db.session.commit()


    from main import models
    with app.app_context():
        db.create_all()

    return app