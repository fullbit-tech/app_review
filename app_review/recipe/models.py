from app_review.extensions import db


class Recipe(db.Model):
    """Instance recipe to run on startup"""
    __tablename__ = "recipe"

    id = db.Column(db.Integer, primary_key=True)
    script = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(155), nullable=False)

    variables = db.relationship(
        "RecipeVariable",
        single_parent=True,
        cascade='all,delete-orphan',
        backref=db.backref("recipe"),
        lazy='joined')

    def __init__(self, name, script, user):
        self.name = name
        self.script = script
        self.user_id = user.id

    @classmethod
    def default_vars(cls):
        return [RecipeVariable('app_dir', '/srv/app')]


class RecipeVariable(db.Model):
    """A variable to be parsed when rendering a recipe"""
    __tablename__ = "recipe_variable"

    recipe_id = db.Column(db.Integer,
                          db.ForeignKey('recipe.id'),
                          primary_key=True)
    name = db.Column(db.String(155), nullable=False, primary_key=True)
    value = db.Column(db.String(155), nullable=True)

    def __init__(self, name, value):
        self.name = name
        self.value = value
