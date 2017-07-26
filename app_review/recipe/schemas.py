from marshmallow import fields, Schema


class RecipeSchema(Schema):
    id = fields.Integer()
    script = fields.Str(required=True)


recipe_schema = RecipeSchema()
