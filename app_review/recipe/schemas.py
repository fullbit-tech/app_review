from marshmallow import fields, Schema, post_load, ValidationError


class RecipeVariableSchema(Schema):
    name = fields.String(required=True, validate=lambda s: s != "")
    value = fields.String(required=True, validate=lambda s: s != "")


class RecipeSchema(Schema):
    id = fields.Integer()
    script = fields.String(required=True, validate=lambda s: s != "")
    name = fields.String(required=True, validate=lambda s: s != "")
    variables = fields.Nested(RecipeVariableSchema, missing=list, many=True)

    @post_load
    def validate_unique_vars(self, data):
        var_names = [v['name'] for v in data['variables']]
        if len(var_names) > len(set(var_names)):
            raise ValidationError(
                'Duplicate Recipe Variable exists', 'variables')


recipe_schema = RecipeSchema()
