from app.blueprints.api import api
from app.blueprints.auth import auth
from app.blueprints.budget_api import budget_api
from app.blueprints.bills_api import bills_api
from app.blueprints.transactions_api import transactions_api
from app.blueprints.accounts_api import accounts_api

from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Banking System API",
        'dom_id': '#swagger-ui',
        'deepLinking': True,
        'defaultModelsExpandDepth': 1,
        'defaultModelExpandDepth': 1,
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)


def init_routes(app):
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(auth, url_prefix="/api")
    app.register_blueprint(budget_api, url_prefix="/api")
    app.register_blueprint(bills_api, url_prefix="/api")
    app.register_blueprint(transactions_api, url_prefix='/api')
    app.register_blueprint(accounts_api, url_prefix='/api')

    app.register_blueprint(swaggerui_blueprint)
