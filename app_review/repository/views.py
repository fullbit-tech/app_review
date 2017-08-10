from flask import Blueprint, g
from flask_restful import Resource, Api, abort
from flask_jwt import current_identity, jwt_required

from app_review.libs.github import GitHub, GitHubException
from app_review.repository.models import RepositoryLink
from app_review.repository.schemas import repository_link_schema
from app_review.extensions import db


repository_api_bp = Blueprint('repository_api', __name__)
repository_api = Api(repository_api_bp)


@repository_api_bp.before_request
def before_request():
    g.user = current_identity


class Repository(Resource):
    """Links and Unlinks Github repositories"""

    def _get_repository(self, owner, repo):
        """Get a repository for a given owner and name"""
        gh = GitHub(access_token=g.user.github_access_token)
        try:
            repository = gh.get_repository(owner, repo)
        except GitHubException:
            abort(400, message="Not Authorized to use that Repository")
        return repository

    def _get_repository_link(self, owner, repo):
        repository = RepositoryLink.query.filter_by(
            owner=owner,
            repository=repo,
            user_id=g.user.id).first()
        if not repository:
            abort(404, message="Repository Link Not Found")
        return repository

    @jwt_required()
    def post(self, owner, repo):
        repository = self._get_repository(owner, repo)
        link = RepositoryLink(owner, repo, g.user)
        db.session.add(link)
        db.session.commit()
        return repository_link_schema.dump(repository)

    @jwt_required()
    def delete(self, owner, repo):
        repo_link = self._get_repository_link(owner, repo)
        db.session.delete(repo_link)
        db.session.commit()
        return {}


class Repositories(Resource):
    """Returns list of repository links"""

    def _get_repository_links(self):
        return RepositoryLink.query.filter_by(user_id=g.user.id)

    @jwt_required
    def get(self):
        repo_links = self._get_repository_links()
        return repository_link_schema.dump(repo_links, many=True)


repository_api.add_resource(Repository, '/<owner>/<repo>')
repository_api.add_resource(Repositories, '')
