from flask import Blueprint, g, request, redirect, current_app
from flask_restful import Resource, Api
from flask_jwt import current_identity, jwt_required

from app_review.extensions import db
from app_review.user.models import User
from app_review.libs.github import GitHub


auth_api_bp = Blueprint('auth_api', __name__)
auth_api = Api(auth_api_bp)


@auth_api_bp.before_request
def before_request():
    g.user = current_identity


def authenticate(email, password):
    """Flask-JWT authorization callback"""
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user


def identity(payload):
    """Flask-JWT identity callback"""
    user_id = payload['identity']
    return User.query.filter_by(id=user_id).first()


class GitHubAuthCallBack(Resource):

    def get(self):
        """Callback for the Github oAuth authorization"""
        code = request.args.get('code')
        state_token = request.args.get('state')
        github = GitHub()
        auth_response = github.authorize_access(code, state_token)
        access_token = auth_response.get('access_token')
        user = User.query.filter_by(
            github_state_token=state_token).first()
        #scope = auth_response.get('scope')
        if access_token is None or not user:
            return redirect(current_app.config['APP_REVIEW_WEB_URL'] +
                            '?github_auth=false');
        user.github_access_token = access_token
        db.session.add(user)
        db.session.commit()
        return redirect(current_app.config['APP_REVIEW_WEB_URL'] +
                        '?github_auth=true')


class GitHubAuth(Resource):

    def _generate_github_auth_uri(self, user):
        """Generates a redirect to github to begin authorization"""
        return ("http://github.com/login/oauth/authorize"
                "?client_id=" "{client_id}&scope={scope}"
                "&state={state}").format(
                    client_id=current_app.config['GITHUB_CLIENT_ID'],
                    scope='user:email,repo',
                    state=user.github_state_token)

    @jwt_required()
    def get(self):
        """Returns a github auth redirect url"""
        return {'url': self._generate_github_auth_uri(g.user)}


auth_api.add_resource(GitHubAuthCallBack, '/github/callback')
auth_api.add_resource(GitHubAuth, '/github')
