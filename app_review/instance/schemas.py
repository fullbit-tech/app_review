from marshmallow import Schema, fields

from app_review.repository.schemas import RepositoryLinkSchema


class InstanceSchema(Schema):
    instance_size = fields.String(default="t2.small", allow_none=True)
    recipe_id = fields.String(allow_none=True)
    repository_link = fields.Nested(RepositoryLinkSchema)
    instance_output = fields.String()

    class Meta:
        fields = ('id', 'instance_id', 'instance_state', 'recipe_id',
                  'instance_size', 'instance_url', 'repository_link',
                  'instance_output')
        dump_only = ('id', 'instance_id', 'instance_state', 'instance_url',
                     'repository_link', 'instance_output')


class PullRequestUser(Schema):
    class Meta:
        fields = ('id', 'login', 'html_url', 'avatar_url')
        dump_only = ('id', 'login', 'html_url', 'avatar_url')


class PullRequestSchema(Schema):
    instance =  fields.Nested(InstanceSchema)
    user = fields.Nested(PullRequestUser)

    class Meta:
        fields = ('id', 'number', 'state', 'body', 'html_url',
                  'title', 'instance', 'user')
        dump_only = ('id', 'number', 'state', 'body', 'html_url',
                     'title', 'instance', 'user')



pull_request_schema = PullRequestSchema()
instance_schema = InstanceSchema()
