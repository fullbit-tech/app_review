from marshmallow import Schema


class PullRequest(Schema):
    class Meta:
        fields = ('state', 'body', 'html_url', 'title')


pull_request_schema = PullRequest()


