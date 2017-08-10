from flask import Blueprint, g, request
from flask_restful import Resource, Api, abort
from flask_jwt import current_identity, jwt_required

from app_review.libs.github import GitHub, GitHubException
from app_review.libs.aws import EC2
from app_review.libs.ssh import SSH
from app_review.extensions import db
from app_review.instance.schemas import (pull_request_schema,
                                         instance_schema)
from app_review.instance.models import PullRequestInstance
from app_review.recipe.models import Recipe
from app_review.repository.models import RepositoryLink


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

    def _get_instance(self, owner, repo, number):
        return PullRequestInstance.query.filter_by(
            github_pull_number=number, user_id=g.user.id,
        ).filter(
            PullRequestInstance.instance_state != 'terminated',
            RepositoryLink.owner == owner,
            RepositoryLink.repository == repo).first()


    def _get_recipe(self, recipe_id):
        recipe = Recipe.query.filter_by(
            id=recipe_id, user_id=g.user.id).first()
        if not recipe:
            abort(400, message="Recipe Not Found")
        return recipe

    def _get_repository_link(self, owner, repo):
        repo = RepositoryLink.query.filter_by(
            owner=owner,
            repository=repo,
            user_id=g.user.id).first()
        if not repo:
            abort(400, message="Repository Not Linked")
        return repo

    @jwt_required()
    def get(self, owner, repo, number):
        """Gets pull request information"""
        pull_request = self._get_pull_request(
            owner, repo, number)
        instance = self._get_instance(owner, repo, number)
        if instance:
            pull_request['instance'] = instance or {}
        return pull_request_schema.dump(pull_request)

    @jwt_required()
    def post(self, owner, repo, number):
        """Starts an instance for a pull request"""
        payload, errors = instance_schema.load(request.get_json())
        if errors:
            return {'errors': errors}, 400

        pull_request = self._get_pull_request(owner, repo, number)
        instance = self._get_instance(owner, repo, number)
        recipe = self._get_recipe(payload['recipe_id'])
        repo_link = self._get_repository_link(owner, repo)

        ec2 = EC2(instance.instance_id if instance else None)
        ec2.start()
        if not instance:
            instance = PullRequestInstance(
                ec2.instance.id,
                ec2.state,
                ec2.instance.instance_type,
                ec2.instance.public_dns_name,
                owner, repo_link, number, g.user, recipe)
        else:
            instance.instance_state = ec2.state
            instance.recipe_id = recipe.id
            instance.instance_size = payload['instance_size']

        pull_request['instance'] = instance
        db.session.add(instance)
        db.session.commit()

        ssh = SSH(instance.instance_url, g.user.github_access_token)
        ssh.wait_for_conn()
        ssh.clone_repository(pull_request['base']['repo']['clone_url'])
        ssh.checkout_branch(pull_request['head']['ref'])
        ssh.run_script(recipe.script)

        return pull_request_schema.dump(pull_request)

    @jwt_required()
    def delete(self, owner, repo, number):
        """Stops or terminates a pull request instance"""
        pull_request = self._get_pull_request(owner, repo, number)
        instance = self._get_instance(owner, repo, number)
        terminate = request.args.get('terminate') == 'true'
        if instance:
            ec2 = EC2(instance.instance_id)
            if terminate:
                ec2.terminate()
            else:
                ec2.stop()
            instance.instance_state = ec2.state
            db.session.add(instance)
            db.session.commit()
        pull_request['instance'] = {} if terminate else instance
        return pull_request_schema.dump(pull_request)


class PullRequests(Resource):

    def _get_pull_requests(self):
        """Get all open pull request from the github API"""
        gh = GitHub(access_token=g.user.github_access_token)
        try:
            pull_requests = gh.get_pull_requests()
        except GitHubException:
            abort(400, message="Pull Requests Not Found")
        return pull_requests

    @jwt_required()
    def get(self):
        pull_requests = self._get_pull_requests()
        return pull_request_schema.dump(pull_requests['items'], many=True)



instance_api.add_resource(
    PullRequest, '/pull-request/<owner>/<repo>/<number>')
instance_api.add_resource(
    PullRequests, '/instance')
