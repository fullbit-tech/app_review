# -*- coding: utf-8 -*-
"""Application configuration."""
import os
import datetime


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('APP_REVIEW_SECRET')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('APP_REVIEW_DATABASE_URI')

    # Github oAuth
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
    GITHUB_SIGNATURE_SECRET = os.environ.get('GITHUB_SIGNATURE_SECRET')

    # JWT Settings
    JWT_EXPIRATION_DELTA = datetime.timedelta(days=1)
    JWT_AUTH_USERNAME_KEY = 'email'

    # AWS API
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_HOST_USERNAME = os.environ.get('AWS_HOST_USERNAME')
    AWS_KEY_FILE = os.environ.get('AWS_KEY_FILE')

    # Celery
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    CELERY_BROKER_URL = 'redis://localhost:6379'


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    #SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/example'
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    DEBUG_TB_ENABLED = True
    APP_REVIEW_WEB_URL = 'http://192.168.2.22:3000'


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
