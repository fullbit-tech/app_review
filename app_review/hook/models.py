from app_review.extensions import db


class GithubHook(db.Model):
    """A Registered Github Web Hook"""
    __tablename__ = "github_web_hook"

    id = db.Column(db.Integer, primary_key=True)
    repository_link_id = db.Column(db.Integer,
        db.ForeignKey('repository_link.id', ondelete='SET NULL'))
    hook_id = db.Column(db.Integer, nullable=False)


