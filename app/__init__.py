from flask import Flask
from os import environ, path
from sqlalchemy_utils import database_exists, create_database
import logging
from .models import db
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from .models.seeders import seed_transaction_categories
from flask_bcrypt import Bcrypt
from app.utils.email import mail

migrate = Migrate()
bcrypt = Bcrypt()


def create_app():
    # env path one level up from here
    basedir = path.abspath(path.dirname(path.dirname(__file__)))
    load_dotenv(path.join(basedir, ".env"))

    app = Flask(__name__)

    # bcrypt
    bcrypt.init_app(app)

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
    from .routes.routes import init_routes
    init_routes(app)

    # init flask-migrate
    migrate.init_app(app, db)

    # init mail service
    app.config['MAIL_SERVER'] = environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = environ.get('MAIL_SENDER')

    mail.init_app(app)

    return app
