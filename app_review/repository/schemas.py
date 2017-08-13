from marshmallow import (Schema, fields,
                         validates_schema, ValidationError)

from app_review.repository.models import RepositoryLink
from app_review.instance.schemas import PullRequestSchema


class RepositoryLinkSchema(Schema):
    repository = fields.String(required=True, validate=lambda s: s != "")
    owner = fields.String(required=True, validate=lambda s: s != "")

    @validates_schema
    def validate_repo_link(self, data):
        repo_link = RepositoryLink.query.filter_by(
            owner=data['owner'], repository=data['repository']).first()
        if repo_link:
            raise ValidationError(
                'Repository is already linked', 'repository')


class RepositoryPullRequestsSchema(Schema):
    respository_link = fields.Nested(RepositoryLinkSchema)
    pull_requests = fields.Nested(PullRequestSchema, many=True)


repository_link_schema = RepositoryLinkSchema()
repository_pull_request_schema = RepositoryPullRequestsSchema()
