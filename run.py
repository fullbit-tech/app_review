# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask.helpers import get_debug_flag

from app_review.app import create_app
from app_review.settings import DevConfig, ProdConfig
from app_review.extensions import celery


CONFIG = DevConfig

app = create_app(CONFIG)
