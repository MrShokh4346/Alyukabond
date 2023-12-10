from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from sqlalchemy import MetaData
from dotenv.main import load_dotenv
import os
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_cors import CORS, cross_origin


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
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config["SECRET_KEY"] = os.environ['SECRET_KEY']
    # app.config["CORS_HEADERS"] = "*"

    cors = CORS(app)

    db.init_app(app=app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from main.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth/v1")

    from main.salafan import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/salafan/v1")

    from main.alyukabond import bp as al_bp
    app.register_blueprint(al_bp, url_prefix="/alyukabond/v1")

    from main.models import Users
    @app.cli.command('adduser')
    def add_category():
        first_name = input("name: ")
        username = input("username: ")
        password = input("password: ")
        role = input("role (a/se/e): ")
        user = Users(first_name=first_name, username=username, role=role, password=password)
        with app.app_context():
            db.session.add(user)
            db.session.commit()


    from main import models
    with app.app_context():
        db.create_all()

    # @app.before_request
    # def option_autoreply():
    #     """ Always reply 200 on OPTIONS request """

    #     if request.method == 'OPTIONS':
    #         resp = app.make_default_options_response()

    #         headers = None
    #         if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
    #             headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']

    #         h = resp.headers

    #         # Allow the origin which made the XHR
    #         h['Access-Control-Allow-Origin'] = request.headers['Origin']
    #         # Allow the actual method
    #         h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
    #         # Allow for 10 seconds
    #         h['Access-Control-Max-Age'] = "10"

    #         # We also keep current headers
    #         if headers is not None:
    #             h['Access-Control-Allow-Headers'] = headers

    #         return resp


    # @app.after_request
    # def set_allow_origin(resp):
    #     """ Set origin for GET, POST, PUT, DELETE requests """

    #     h = resp.headers

    #     # Allow crossdomain for other HTTP Verbs
    #     if request.method != 'OPTIONS' and 'Origin' in request.headers:
    #         h['Access-Control-Allow-Origin'] = request.headers['Origin']


    #     return resp


    return app