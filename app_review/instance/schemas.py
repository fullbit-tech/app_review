from marshmallow import Schema, fields


class InstanceSchema(Schema):
    intance_size = fields.String(required=True,
                                 validate=lambda s: s != "")
    recipe_id = fields.String(required=True,
                              validate=lambda s: s != "")

    class Meta:
        fields = ('instance_id', 'instance_state', 'recipe_id',
                  'instance_size', 'instance_url')
        dump_only = ('instance_id', 'instance_state', 'instance_url')


class PullRequestUser(Schema):
    class Meta:
        fields = ('login', 'html_url', 'avatar_url')
        dump_only = ('login', 'html_url', 'avatar_url')


class PullRequestSchema(Schema):
    instance =  fields.Nested(InstanceSchema)
    user = fields.Nested(PullRequestUser)

    class Meta:
        fields = ('number', 'state', 'body', 'html_url',
                  'title', 'instance', 'user')
        dump_only = ('number', 'state', 'body', 'html_url',
                     'title', 'instance', 'user')



pull_request_schema = PullRequestSchema()
instance_schema = InstanceSchema()
