from operator import itemgetter

from flask import Blueprint, g, request
from flask_restful import Resource, Api, abort
from flask_jwt import current_identity, jwt_required

from app_review.libs.github import GitHub, GitHubException
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

    def _get_pull_request(self, repo_link, number):
        """Get a pull request from the github API"""
        gh = GitHub(access_token=g.user.github_access_token)
        try:
            pull_request = gh.get_pull_request(
                repo_link.owner, repo_link.repository, number)
        except GitHubException:
            abort(404, message="Pull Request Not Found")
        return pull_request

    def _notify_pull_request(self, comments_url, instance_url):
        """Create a comment on the pull request to indicate that an
           instance has been created for it.
        """
        gh = GitHub(access_token=g.user.github_access_token)
        message = ("An App Review instance has been created for this "
                   "pull request: [{url}]({url})".format(
                       url=instance_url))
        try:
            gh.create_comment(comments_url, message)
        except GitHubException:
            pass

    def _get_instance(self, id):
        instance = PullRequestInstance.query.filter_by(
            id=id, user_id=g.user.id).first()
        if not instance:
            abort(400, message="Instance Not Found")
        return instance

    def _get_recipe(self, recipe_id):
        recipe = Recipe.query.filter_by(
            id=recipe_id, user_id=g.user.id).first()
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
    def get(self, instance_id):
        """Gets pull request information"""
        instance = self._get_instance(instance_id)
        pull_request = self._get_pull_request(
            instance.repository_link, instance.github_pull_number)
        pull_request['instance'] = instance
        return pull_request_schema.dump(pull_request)

    @jwt_required()
    def post(self, instance_id):
        """Starts an instance for a pull request"""
        instance = self._get_instance(instance_id)
        payload, errors = instance_schema.load(request.get_json())
        pull_request = self._get_pull_request(
            instance.repository_link, instance.github_pull_number)
        recipe = self._get_recipe(payload['recipe_id'])
        _should_provision = instance.instance_id is None

        if not errors:
            instance_output = [['starting instance...']]
            instance.start(commit=False)
            instance_output.append(['instance successfully started'])
            instance.recipe = recipe

            ssh = SSH(instance.instance_url, g.user.github_access_token)

            try:
                ssh.wait_for_conn()
                instance_output.append(['cloning repository...'])
                ssh.clone_repository(pull_request['base']['repo']['clone_url'])
                instance_output.append(['checking out pull request branch...'])
                ssh.checkout_branch(pull_request['head']['ref'])
            except SystemExit:
                instance_output.append(
                    ['an error occured during startup, terminating instance...'])
                instance.terminate(commit=False)
                instance_output.append(['instance terminated'])

            if _should_provision and recipe and not pull_request.get('error'):
                instance_output.append(['running recipe...'])
                try:
                    instance_output.append(
                        ssh.run_script(recipe.render_script()))
                except SystemExit:
                    instance_output.append(
                        ['recipe failed, terminating instance'])
                    instance.terminate(commit=False)
                    instance_output.append(['instance terminated'])
                else:
                    self._notify_pull_request(
                        pull_request['comments_url'],
                        'http://' + instance.instance_url)

        db.session.add(instance)
        db.session.commit()

        instance.instance_output = '\n'.join(
                [l for logs in instance_output for l in logs])
        pull_request['instance'] = instance
        data, _ = pull_request_schema.dump(pull_request)

        if errors:
            data['errors'] = errors
            return data, 400
        return data


    @jwt_required()
    def delete(self, instance_id):
        """Stops or terminates a pull request instance"""
        instance = self._get_instance(instance_id)
        instance_output = []
        pull_request = self._get_pull_request(
            instance.repository_link, instance.github_pull_number)
        terminate = request.args.get('terminate') == 'true'
        if terminate:
            instance_output.append('terminating...')
            instance.terminate()
            instance_output.append('successfully terminated')
        else:
            instance_output.append('stopping...')
            instance.stop()
            instance_output.append('successfully stopped')
        instance.instance_output = '\n'.join(
                [log for log in instance_output])
        pull_request['instance'] = instance
        return pull_request_schema.dump(pull_request)


class PullRequests(Resource):

    def _get_pull_requests(self, owner, repo):
        """Get all open pull request from the github API"""
        gh = GitHub(access_token=g.user.github_access_token)
        try:
            pull_requests = gh.get_pull_requests(owner, repo)
        except GitHubException:
            abort(400, message="Pull Requests Not Found")
        return pull_requests

    @jwt_required()
    def get(self):
        pull_requests = []
        filter_active = request.args.get('active') == 'true'
        for repo_link in RepositoryLink.query.filter_by(user_id=g.user.id):
            github_pulls = sorted(
                self._get_pull_requests(repo_link.owner,
                                        repo_link.repository),
                key=itemgetter('number'), reverse=True)
            for i, pull_request in enumerate(github_pulls):
                instance = PullRequestInstance.get_or_create(
                    repo_link, str(pull_request['number']))
                if filter_active and not instance.instance_id:
                    continue
                pull_request['instance'] = instance
                pull_requests.append(pull_request)
        return pull_request_schema.dump(pull_requests, many=True)



instance_api.add_resource(
    PullRequest, '/instance/<int:instance_id>')
instance_api.add_resource(
    PullRequests, '/instance')
