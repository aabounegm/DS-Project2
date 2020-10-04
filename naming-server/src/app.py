"""Flask application factory."""

from importlib import import_module
import logging
import logging.config

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from src.extensions import mongo
from src.blueprints import all_blueprints

log = logging.getLogger(__name__)


def create_app():
    """Create a Flask application"""
    app = Flask(__name__)
    mongo.init_app(app)

    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'datefmt': '%d/%m %H:%M:%S',
                'format': '[%(asctime)s] [%(levelname)8s] %(message)s (%(name)s:%(lineno)s)',
            }
        },
        'handlers': {
            'stderr': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': 'DEBUG',
            },
        },
        'loggers': {
            'werkzeug': {
                'handlers': ['stderr'],
                'propagate': False,
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['stderr']
        },
        'disable_existing_loggers': False,
    })

    for blueprint in all_blueprints:
        import_module(blueprint.import_name)
        app.register_blueprint(blueprint)

    # Needed when running behind Nginx under Docker for authorization
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
    return app
