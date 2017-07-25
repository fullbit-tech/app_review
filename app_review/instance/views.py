from flask import Blueprint, g
from flask_restful import Resource, Api, abort
from flask_jwt import current_identity, jwt_required

from app_review.libs.github import GitHub, GitHubException
from app_review.libs.aws import EC2
from app_review.extensions import db
from app_review.instance.schemas import pull_request_schema
from app_review.instance.models import PullRequestInstance


instance_api_bp = Blueprint('instance_api', __name__)
instance_api = Api(instance_api_bp)


@instance_api_bp.before_request
def before_request():
    g.user = current_identity


class PullRequest(Resource):

    def _get_pull_request(self, owner, repo, number):
        """Get a pull request from the github API"""
        gh = GitHub(access_token=g.user.github_access_token)
        try:
            pull_request = gh.get_pull_request(
                owner, repo, number)
        except GitHubException:
            abort(404, message="Not Found")
        return pull_request

    def _get_instance(self, owner, repo, number, user):
        return PullRequestInstance.query.filter_by(
            github_owner=owner, github_repository=repo,
            github_pull_number=number, user_id=user.id,
        ).filter(
            PullRequestInstance.instance_state != 'terminated').first()

    @jwt_required()
    def get(self, owner, repo, number):
        """Gets pull request information"""
        pull_request = self._get_pull_request(
            owner, repo, number)
        return pull_request_schema.dump(pull_request)

    @jwt_required()
    def post(self, owner, repo, number):
        """Starts an instance for a pull request"""
        self._get_pull_request(owner, repo, number)
        instance = self._get_instance(owner, repo, number, g.user)
        ec2 = EC2(instance.instance_id if instance else None)
        ec2.start()
        if not instance:
            instance = PullRequestInstance(
                ec2.instance.id, ec2.state,
                ec2.instance.instance_type,
                ec2.instance.public_dns_name,
                owner, repo, number, g.user,
            )
        else:
            instance.state = ec2.state
        db.session.add(instance)
        db.session.commit()
        return dict(
            url=instance.instance_url,
            state=instance.instance_state,
        )

    @jwt_required()
    def delete(self, owner, repo, number):
        self._get_pull_request(owner, repo, number)
        instance = self._get_instance(owner, repo, number, g.user)
        if instance:
            ec2 = EC2(instance.instance_id)
            ec2.terminate()
            instance.instance_state = 'terminated'
            db.session.add(instance)
            db.session.commit()
        return dict(message="success")


instance_api.add_resource(
    PullRequest, '/pull-request/<owner>/<repo>/<number>')
