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
    def repository_link_id(cls):
        return db.Column(db.Integer,
            db.ForeignKey('repository_link.id', ondelete='SET NULL'))

    @declared_attr
    def recipe_id(cls):
        return db.Column(db.Integer,
             db.ForeignKey('recipe.id', ondelete='SET NULL'),
             nullable=True)

    def __init__(self, instance_id, instance_state,
                 instance_size, instance_url, user,
                 recipe, repository_link, **kwargs):
        super(Instance, self).__init__(**kwargs)
        self.instance_id = instance_id
        self.instance_state = instance_state
        self.instance_size = instance_size
        self.instance_url = instance_url
        self.user_id = user.id
        self.recipe_id = recipe.id
        self.repository_link_id = repository_link.id


class PullRequestInstance(Instance, db.Model):
    """An instance created for a pull request"""
    __tablename__ = "pull_request_instance"

    id = db.Column(db.Integer, primary_key=True)
    github_pull_number = db.Column(db.String)

    def __init__(self, instance_id, instance_state, instance_size,
                 instance_url, owner, repository_link, pull_number, user,
                 recipe):
        super(PullRequestInstance, self).__init__(
            repository_link=repository_link, user=user,
            instance_id=instance_id, instance_state=instance_state,
            instance_size=instance_size, instance_url=instance_url,
            recipe=recipe)
        self.github_pull_number = pull_number
