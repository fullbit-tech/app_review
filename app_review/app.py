# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask, render_template
from flask_jwt import JWT

from app_review.extensions import db, github
from app_review.settings import ProdConfig

from app_review.auth.views import (auth_api_bp, auth_api,
                                   authenticate, identity)
from app_review.user.views import user_api_bp, user_api
from app_review.user.models import User


def create_app(config_object=ProdConfig):
    """An application factory.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_shellcontext(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    github.init_app(app)
    JWT(app, authenticate, identity)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(auth_api_bp, url_prefix='/auth')
    app.register_blueprint(user_api_bp, url_prefix='/user')


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'User': User,
        }

    app.shell_context_processor(shell_context)
