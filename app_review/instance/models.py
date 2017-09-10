from sqlalchemy.ext.declarative import declared_attr

from app_review.libs.aws import EC2
from app_review.extensions import db


class Instance(object):
    """Mixin for instance models"""

    instance_id = db.Column(db.String, nullable=True)
    instance_state = db.Column(db.String, default="dormant")
    instance_size = db.Column(db.String, nullable=True)
    instance_url = db.Column(db.String, nullable=True)

    def __init__(self, *args, **kwargs):
        super(Instance, self).__init__(*args, **kwargs)
        self.instance_output = ''

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


class PullRequestInstance(Instance, db.Model):
    """An instance created for a pull request"""
    __tablename__ = "pull_request_instance"

    id = db.Column(db.Integer, primary_key=True)
    github_pull_number = db.Column(db.String)

    @classmethod
    def get_or_create(cls, repo_link, pull_number, **kwargs):
        instance = cls.query.filter_by(
            repository_link_id=repo_link.id,
            github_pull_number=pull_number).first()
        if not instance:
            instance = PullRequestInstance(
                repository_link_id=repo_link.id,
                github_pull_number=pull_number,
                user_id=repo_link.user.id)
            db.session.add(instance)
            db.session.commit()
        return instance

    def start(self, commit=True):
        """Start or creates and starts the associated ec2 instance"""
        ec2 = EC2(self.instance_id if self.instance_id else None)
        ec2.start()
        self.instance_id = ec2.instance.id
        self.instance_state = ec2.state
        self.instance_size = ec2.instance.instance_type
        self.instance_url = ec2.instance.public_dns_name
        if commit:
            db.session.add(self)
            db.session.commit()

    def terminate(self, commit=True):
        """Terminates the associated ec2 instance"""
        ec2 = EC2(self.instance_id)
        ec2.terminate()
        self.instance_state = 'dormant'
        self.instance_size = None
        self.instance_id = None
        self.instance_url = None
        if commit:
            db.session.add(self)
            db.session.commit()

    def stop(self, commit=True):
        """Stops the associated ec2 instance"""
        ec2 = EC2(self.instance_id)
        ec2.stop()
        self.instance_state = ec2.state
        if commit:
            db.session.add(self)
            db.session.commit()
