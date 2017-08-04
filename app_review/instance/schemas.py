from marshmallow import Schema, fields


class InstanceSchema(Schema):
    instance_size = fields.String(required=True)
    recipe_id = fields.Integer(required=True)

    class Meta:
        fields = ('instance_id', 'instance_state', 'recipe_id',
                  'instance_size', 'instance_url')
        dump_only = ('instance_id', 'instance_state', 'instance_url')


class PullRequestSchema(Schema):
    class Meta:
        fields = ('state', 'body', 'html_url', 'title', 'instance')
        dump_only = ('state', 'body', 'html_url', 'title', 'instance')

    instance = fields.Nested(InstanceSchema)


pull_request_schema = PullRequestSchema()
instance_schema = InstanceSchema()


