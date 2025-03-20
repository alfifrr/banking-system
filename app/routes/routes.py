from app.blueprints.api import api
from app.blueprints.auth import auth


def init_routes(app):
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(auth, url_prefix="/api")
