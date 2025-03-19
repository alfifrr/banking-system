from app.blueprints.api import api


def init_routes(app):
    app.register_blueprint(api, url_prefix="/api")
