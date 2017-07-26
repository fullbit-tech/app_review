from flask_sqlalchemy import SQLAlchemy
from flask_jwt import JWT
from flask_migrate import Migrate


db = SQLAlchemy()
jwt = JWT
migrate = Migrate()
