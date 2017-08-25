from flask_sqlalchemy import SQLAlchemy
from flask_jwt import JWT
from flask_migrate import Migrate
from flask_cors import CORS
from flask_celery import Celery


celery = Celery()
db = SQLAlchemy()
jwt = JWT
migrate = Migrate()
cors = CORS()
