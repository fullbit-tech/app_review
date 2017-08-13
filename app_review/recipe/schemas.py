from marshmallow import (fields, Schema, post_load,
                         ValidationError, validates)

from app_review.recipe.models import RECIPE_CONSTANTS


class RecipeVariableSchema(Schema):
    name = fields.String(required=True, validate=lambda s: s != "")
    value = fields.String(required=True, validate=lambda s: s != "")

    @validates('name')
    def validate_name(self, name):
        if name in RECIPE_CONSTANTS:
            raise ValidationError(
                '{} is a reserved variable name'.format(name))


class RecipeSchema(Schema):
    id = fields.Integer()
    script = fields.String(required=True, validate=lambda s: s != "")
    name = fields.String(required=True, validate=lambda s: s != "")
    variables = fields.Nested(RecipeVariableSchema, missing=list, many=True)


recipe_schema = RecipeSchema()
