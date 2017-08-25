from marshmallow import Schema


class PullRequestHookSchema(Schema):
    class Meta:
        fields = ('id', 'action', 'number', 'pull_request', 'sender')


pull_request_hook_schema = PullRequestHookSchema()
