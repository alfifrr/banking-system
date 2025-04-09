from app.blueprints.api import api
from app.blueprints.auth import auth
from app.blueprints.budget_api import budget_api
from app.blueprints.bills_api import bills_api
from app.blueprints.transactions_api import transactions_api
from app.blueprints.accounts_api import accounts_api


def init_routes(app):
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(auth, url_prefix="/api")
    app.register_blueprint(budget_api, url_prefix="/api")
    app.register_blueprint(bills_api, url_prefix="/api")
    app.register_blueprint(transactions_api, url_prefix='/api')
    app.register_blueprint(accounts_api, url_prefix='/api')
