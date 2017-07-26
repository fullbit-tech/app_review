from sqlalchemy.ext.declarative import declared_attr
from app_review.extensions import db


class Instance(object):
    """Mixin for instance models"""

    instance_id = db.Column(db.String)
    instance_state = db.Column(db.String)
    instance_size = db.Column(db.String)
    instance_url = db.Column(db.String)

    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey('user.id'))

    @declared_attr
    def recipe_id(cls):
        return db.Column(
            db.Integer, db.ForeignKey('recipe.id'), nullable=True)

    def __init__(self, instance_id, instance_state,
                 instance_size, instance_url, user, recipe, **kwargs):
        super(Instance, self).__init__(**kwargs)
        self.instance_id = instance_id
        self.instance_state = instance_state
        self.instance_size = instance_size
        self.instance_url = instance_url
        self.user_id = user.id
        self.recipe_id = recipe.id


class Repository(Instance):
    """Mixing for repository models"""
    github_owner = db.Column(db.String)
    github_repository = db.Column(db.String)

    def __init__(self, owner, repository, **kwargs):
        super(Repository, self).__init__(**kwargs)
        self.github_owner = owner
        self.github_repository = repository


class PullRequestInstance(Repository, Instance, db.Model):
    """An instance created for a pull request"""
    __tablename__ = "pull_request_instance"

    id = db.Column(db.Integer, primary_key=True)
    github_pull_number = db.Column(db.String)

    def __init__(self, instance_id, instance_state, instance_size,
                 instance_url, owner, repository, pull_number, user,
                 recipe):
        super(PullRequestInstance, self).__init__(
            owner=owner, repository=repository, user=user,
            instance_id=instance_id, instance_state=instance_state,
            instance_size=instance_size, instance_url=instance_url,
            recipe=recipe)
        self.github_pull_number = pull_number
