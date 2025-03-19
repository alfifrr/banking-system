from flask import Flask
from os import environ, path
from sqlalchemy_utils import database_exists, create_database
import logging
from .models.user import db
from dotenv import load_dotenv
from pathlib import Path
from .routes.routes import init_routes


def create_app():
    basedir = path.abspath(path.dirname(path.dirname(__file__)))
    print(basedir)
    load_dotenv(path.join(basedir, ".env"))
    # env_path = Path(__file__).parent.parent / ".env"
    # load_dotenv(env_path)

    app = Flask(__name__)

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
            logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise

    # init routes
    init_routes(app)

    return app
