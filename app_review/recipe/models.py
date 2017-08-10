from app_review.extensions import db


class Recipe(db.Model):
    """Instance recipe to run on startup"""
    __tablename__ = "recipe"

    id = db.Column(db.Integer, primary_key=True)
    script = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(155), nullable=False)

    def __init__(self, user, script, name):
        self.user_id = user.id
        self.script = script
        self.name = name


class RecipeVariable(db.Model):
    """A variable to be parsed when rendering a recipe"""
    __tablename__ = "recipe_variable"

    recipe_id = db.Column(db.Integer,
                          db.ForeignKey('recipe.id'),
                          primary_key=True)
    name = db.Column(db.String(155), nullable=False)
    value = db.Column(db.String(155), nullable=True)

    def __init__(self, recipe, name, value):
        self.recipe_id = recipe.id
        self.name = name
        self.value = value

