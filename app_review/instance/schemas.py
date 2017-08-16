from marshmallow import Schema, fields

from app_review.repository.schemas import RepositoryLinkSchema


class InstanceSchema(Schema):
    intance_size = fields.String(required=True,
                                 validate=lambda s: s != "")
    recipe_id = fields.String(required=True,
                              validate=lambda s: s != "")
    repository_link = fields.Nested(RepositoryLinkSchema)

    class Meta:
        fields = ('id', 'instance_id', 'instance_state', 'recipe_id',
                  'instance_size', 'instance_url', 'repository_link')
        dump_only = ('id', 'instance_id', 'instance_state', 'instance_url',
                     'repository_link')


class PullRequestUser(Schema):
    class Meta:
        fields = ('login', 'html_url', 'avatar_url')
        dump_only = ('login', 'html_url', 'avatar_url')


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
