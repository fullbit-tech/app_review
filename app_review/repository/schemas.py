from marshmallow import Schema, fields


class RepositoryLinkSchema(Schema):
    name = fields.String(required=True, allow_none=False)
    owner = fields.String(required=True, allow_none=False)

    class Meta:
        dump_only = ('name', 'owner')


repository_link_schema = RepositoryLinkSchema()
