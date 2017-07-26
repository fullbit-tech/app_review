from flask import Blueprint, g, request
from flask_restful import Resource, Api, abort
from flask_jwt import current_identity, jwt_required

from app_review.libs.github import GitHub, GitHubException
from app_review.libs.aws import EC2
from app_review.extensions import db
from app_review.instance.schemas import pull_request_schema
from app_review.instance.models import PullRequestInstance
from app_review.recipe.models import Recipe


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
            abort(404, message="Pull Request Not Found")
        return pull_request

    def _get_instance(self, owner, repo, number, user):
        return PullRequestInstance.query.filter_by(
            github_owner=owner, github_repository=repo,
            github_pull_number=number, user_id=user.id,
        ).filter(
            PullRequestInstance.instance_state != 'terminated').first()

    def _get_recipe(self, recipe_id, user):
        recipe = Recipe.query.filter_by(
            id=recipe_id, user_id=user.id).first()
        if not recipe:
            abort(500, message="Recipe Not Found")
        return recipe

    @jwt_required()
    def get(self, owner, repo, number):
        """Gets pull request information"""
        pull_request = self._get_pull_request(
            owner, repo, number)
        return pull_request_schema.dump(pull_request)

    @jwt_required()
    def post(self, owner, repo, number):
        """Starts an instance for a pull request"""
        payload = request.get_json()
        self._get_pull_request(owner, repo, number)
        recipe = None
        recipe_id = payload['recipe']

        instance = self._get_instance(owner, repo, number, g.user)
        if recipe_id:
            recipe = self._get_recipe(recipe_id, g.user)

        ec2 = EC2(instance.instance_id if instance else None)
        ec2.start(recipe.script if recipe else None)
        if not instance:
            instance = PullRequestInstance(
                ec2.instance.id,
                ec2.state,
                ec2.instance.instance_type,
                ec2.instance.public_dns_name,
                owner, repo, number, g.user, recipe)
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
        """Stops or terminates a pull request instance"""
        self._get_pull_request(owner, repo, number)
        instance = self._get_instance(owner, repo, number, g.user)
        terminate = request.args.get('terminate')
        if instance:
            ec2 = EC2(instance.instance_id)
            if terminate:
                ec2.terminate()
            else:
                ec2.stop()
            instance.instance_state = ec2.state
            db.session.add(instance)
            db.session.commit()
        return dict(message="success")


instance_api.add_resource(
    PullRequest, '/pull-request/<owner>/<repo>/<number>')
