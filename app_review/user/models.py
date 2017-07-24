import uuid
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
from app_review.extensions import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    github_access_token = db.Column(db.String, unique=True,
                                    nullable=True)
    github_state_token = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)
        self.set_github_state()

    def check_password(self, password):
        """Compare a string versus a hashed password"""
        return check_password_hash(self.password, password)

    def set_password(self, password):
        """Create a salted and hashed password given a string"""
        self.password = generate_password_hash(password)

    def set_github_state(self):
        """Create a random token to match a
           callback response with a user"""
        self.github_state_token = uuid.uuid4().hex
