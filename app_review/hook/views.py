from flask import Blueprint, g, request
from flask_restful import Resource, Api, abort
from flask_jwt import current_identity, jwt_required

from app_review.libs.github import GitHub, GitHubException
from app_review.hook.schemas import pull_request_hook_schema
from app_review.instance.models import PullRequestInstance
from app_review.instance.tasks import pull_synchronize


hook_api_bp = Blueprint('hook_api', __name__)
hook_api = Api(hook_api_bp)


@hook_api_bp.before_request
def before_request():
    g.user = current_identity


def github_verified(f):
    def wrapper(*args, **kwargs):
        signature = request.headers.get('X-Hub-Signature')
        if signature and GitHub().verify_signature(
                signature, request.get_data(as_text=True)):
            return f(*args, **kwargs)
        abort(403, message="Not Authorized")

    return wrapper


class GithubPullRequestHook(Resource):

    @jwt_required()
    @github_verified
    def post(self):
        """A webhook callback endpoint for github pull request syncs"""
        data, errors = pull_request_hook_schema.load(request.get_json())
        if data.get('action') == 'synchronize':
            owner, repo = tuple(
                data['pull_request']['repo']['full_name'].split('/'))
            number = data['number']
            hook_owner = data['sender']['login']
            instances = PullRequestInstance.query.filter(
                PullRequestInstance.repository_link.has(owner=owner),
                PullRequestInstance.repository_link.has(repository=repo),
                PullRequestInstance.repository_link.user.has(github_username=hook_owner),
                PullRequestInstance.github_pull_number == str(number),
                PullRequestInstance.instance_state == 'running')
            for instance in instances:
                pull_synchronize.delay(instance.id)


hook_api.add_resource(GithubPullRequestHook, '/github/pull-request')
