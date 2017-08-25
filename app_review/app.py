# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask

from app_review.extensions import db, jwt, migrate, cors, celery
from app_review.settings import ProdConfig

from app_review.auth.views import (auth_api_bp, auth_api,
                                   authenticate, identity)

from app_review.user.models import User
from app_review.user.views import user_api_bp, user_api

from app_review.instance.models import PullRequestInstance
from app_review.instance.views import instance_api_bp, instance_api

from app_review.recipe.models import (Recipe, RecipeDropIn,
                                      RecipeVariable)
from app_review.recipe.views import recipe_api_bp, recipe_api

from app_review.repository.models import RepositoryLink
from app_review.repository.views import repository_api_bp, repository_api

from app_review.hook.views import hook_api_bp, hook_api
from app_review.hook.models import GithubHook



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
    jwt(app, authenticate, identity)
    migrate.init_app(app, db)
    cors.init_app(app)
    celery.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(auth_api_bp, url_prefix='/auth')
    app.register_blueprint(user_api_bp, url_prefix='/user')
    app.register_blueprint(instance_api_bp)
    app.register_blueprint(recipe_api_bp, url_prefix="/recipe")
    app.register_blueprint(repository_api_bp, url_prefix="/repository")
    app.register_blueprint(hook_api_bp, url_prefix="/hook")


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'User': User,
            'PullRequestInstance': PullRequestInstance,
            'Recipe': Recipe,
            'RecipeVariable': RecipeVariable,
            'RecipeDropIn': RecipeDropIn,
            'RepositoryLink': RepositoryLink,
            'GithubHook': GithubHook,
        }

    app.shell_context_processor(shell_context)
