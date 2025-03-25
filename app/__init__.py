from flask import Flask
from os import environ, path
from sqlalchemy_utils import database_exists, create_database
import logging
from .models import db
from dotenv import load_dotenv
from .routes.routes import init_routes
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from .models.seeders import seed_transaction_categories

migrate = Migrate()


def create_app():
    # env path one level up from here
    basedir = path.abspath(path.dirname(path.dirname(__file__)))
    print(basedir)
    load_dotenv(path.join(basedir, ".env"))

    app = Flask(__name__)

    # jwt
    app.config["JWT_SECRET_KEY"] = environ.get("JWT_SECRET_KEY")
    jwt = JWTManager(app)

    # pg db creation
    url = environ.get("POSTGRESQL_URL")
    if not url:
        raise ValueError("POSTGRESQL_URL not set in environment variables")
    try:
        if not database_exists(url):
            create_database(url)
            logging.info("Database created successfully")
        app.config["SQLALCHEMY_DATABASE_URI"] = url
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        with app.app_context():
            db.create_all()
            seed_transaction_categories()  # add default categories
            logging.info("Database tables created successfully")

    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise

    # init routes
    init_routes(app)

    # init flask-migrate
    migrate.init_app(app, db)

    return app
