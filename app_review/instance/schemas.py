from marshmallow import Schema, fields


class InstanceSchema(Schema):
    class Meta:
        fields = ('instance_id', 'instance_state',
                  'instance_size', 'instance_url')


class PullRequestSchema(Schema):
    class Meta:
        fields = ('state', 'body', 'html_url', 'title', 'instance')

    instance = fields.Nested(InstanceSchema)


pull_request_schema = PullRequestSchema()


