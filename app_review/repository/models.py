from app_review.extensions import db


class RepositoryLink(db.Model):
    """Repository Links"""
    __tablename__ = "repository_link"

    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String)
    repository = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    pull_requests = db.relationship(
        "PullRequestInstance",
        single_parent=True,
        cascade='all,delete-orphan',
        backref=db.backref("repository_link"),
        lazy='joined')

    user = db.relationship(
        "User",
        single_parent=True,
        cascade='all,delete-orphan',
        backref=db.backref("repository_links"))

    def __init__(self, owner, repo, user):
        self.owner = owner
        self.repository = repo
        self.user_id = user.id
