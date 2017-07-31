from flask_sqlalchemy import SQLAlchemy
from flask_jwt import JWT
from flask_migrate import Migrate
from flask_cors import CORS


db = SQLAlchemy()
jwt = JWT
migrate = Migrate()
cors = CORS()
