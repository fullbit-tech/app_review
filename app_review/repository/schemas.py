from marshmallow import (Schema, fields,
                         validates_schema, ValidationError)

from app_review.repository.models import RepositoryLink


class RepositoryLinkSchema(Schema):
    id = fields.Integer(required=True)
    repository = fields.String(required=True, validate=lambda s: s != "")
    owner = fields.String(required=True, validate=lambda s: s != "")

    @validates_schema
    def validate_repo_link(self, data):
        repo_link = RepositoryLink.query.filter_by(
            owner=data['owner'], repository=data['repository']).first()
        if repo_link:
            raise ValidationError(
                'Repository is already linked', 'repository')


repository_link_schema = RepositoryLinkSchema()
