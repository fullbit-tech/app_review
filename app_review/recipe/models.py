from app_review.extensions import db


class Recipe(db.Model):
    """Instance recipe to run on startup"""
    __tablename__ = "recipe"

    id = db.Column(db.Integer, primary_key=True)
    script = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, user, script):
        self.user_id = user.id
        self.script = script

