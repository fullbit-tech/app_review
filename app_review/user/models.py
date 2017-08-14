import uuid
from enum import Enum
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
from app_review.extensions import db
from app_review.instance.models import PullRequestInstance


class UserStatus(Enum):
    active = 1
    inactivate = 2


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, default=UserStatus.active.value)
    email = db.Column(db.String, unique=True)
    github_access_token = db.Column(db.String, unique=True,
                                    nullable=True)
    github_state_token = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)
        self.set_github_state()

    @property
    def github_verified(self):
        """If a user has authorized their github account"""
        return self.github_access_token is not None

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

    def deactivate(self):
        instances = PullRequestInstance.query.filter_by(
            user_id=self.id).filter(
                PullRequestInstance.instance_state != 'terminated')
        for instance in instances:
            instance.terminate()
        self.status = UserStatus.inactivate.value
        db.session.add(self)
        db.session.commit()
