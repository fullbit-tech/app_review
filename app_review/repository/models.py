from app_review.extensions import db


class RepositoryLink(db.Model):
    """Repository Links"""
    __tablename__ = "repository_link"

    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String)
    repository = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, owner, repo, user):
        self.owner = owner
        self.repository = repo
        self.user_id = user.id



