"""Flask application factory."""

from importlib import import_module

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from src.extensions import cors
from src.blueprints import all_blueprints


def create_app():
    """Create a Flask application"""
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    cors.init_app(app)

    for blueprint in all_blueprints:
        import_module(blueprint.import_name)
        app.register_blueprint(blueprint)

    # Needed when running behind Nginx under Docker for authorization
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
    return app
