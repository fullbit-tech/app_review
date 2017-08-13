from flask import Blueprint, g, request
from flask_restful import Resource, Api, abort
from flask_jwt import current_identity, jwt_required


from app_review.recipe.models import Recipe, RecipeVariable
from app_review.recipe.schemas import recipe_schema
from app_review.extensions import db


recipe_api_bp = Blueprint('recipe_api', __name__)
recipe_api = Api(recipe_api_bp)


@recipe_api_bp.before_request
def before_request():
    g.user = current_identity


class RecipeAPI(Resource):
    """Specific recipe endpoints"""

    def _get_recipe(self, recipe_id):
        """Gets a recipe by id for a user"""
        recipe = Recipe.query.filter_by(
            id=recipe_id, user_id=g.user.id).first()
        if not recipe:
            abort(404, message="Not Found")
        return recipe

    @jwt_required()
    def get(self, recipe_id):
        """Returns a recipe"""
        recipe = self._get_recipe(recipe_id)
        return recipe_schema.dump(recipe)

    @jwt_required()
    def put(self, recipe_id):
        """Returns a recipe"""
        recipe = self._get_recipe(recipe_id)
        data, errors = recipe_schema.load(request.get_json())
        if errors:
            return {'errors': errors}, 400
        recipe.name = data['name']
        recipe.script = data['script']
        recipe.variables = [RecipeVariable(v['name'], v['value'])
                            for v in data['variables']]
        db.session.add(recipe)
        db.session.commit()
        return recipe_schema.dump(recipe)

    @jwt_required()
    def delete(self, recipe_id):
        """Deletes a recipe"""
        recipe = self._get_recipe(recipe_id)
        db.session.delete(recipe)
        db.session.commit()
        return {}


class RecipesAPI(Resource):
    """Genral recipe endpoints"""

    @jwt_required()
    def get(self):
        """Gets all available recipes for a user"""
        recipes = Recipe.query.filter_by(user_id=g.user.id)
        return recipe_schema.dump(recipes, many=True)

    @jwt_required()
    def post(self):
        """Creates a new recipe for a user"""
        payload, errors = recipe_schema.load(request.get_json())
        if errors:
            return {'errors': errors}, 400
        recipe = Recipe(payload['name'], payload['script'], g.user)
        recipe.variables = [RecipeVariable(v['name'], v['value'])
                            for v in payload['variables']]
        db.session.add(recipe)
        db.session.commit()
        return recipe_schema.dump(recipe)


recipe_api.add_resource(RecipeAPI, '/<int:recipe_id>')
recipe_api.add_resource(RecipesAPI, '')
