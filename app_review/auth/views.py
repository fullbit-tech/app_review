from flask import Blueprint, session, g, current_app, redirect, request
from flask_restful import Resource, Api
import requests

from app_review.extensions import db
from app_review.user.models import User
from app_review.libs.github import GitHub


auth_api_bp = Blueprint('auth_api', __name__)
auth_api = Api(auth_api_bp)


@auth_api_bp.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


class GitHub(object):
    def __init__(self, scope='user:email,repo'):
        self.github_uri = 'https://github.com'
        self.github_api_uri = 'https://api.github.com'
        self.client_id = current_app.config['GITHUB_CLIENT_ID']
        self.client_secret = current_app.config['GITHUB_CLIENT_SECRET']
        self.scope = 'user:email,repo'

    def authorize(self):
        params = dict(scope=self.scope, client_id=self.client_id)
        return redirect((
            '{git_uri}/login/oauth/authorize'
            '?scope={scope}&client_id={client_id}').format(
                git_uri=self.github_uri,
                scope=self.scope,
                client_id=self.client_id),
            code=302)

    def authorize_access(self, code):
        data = dict(client_id=self.client_id,
                    client_secret=self.client_secret,
                    code=code)
        r = requests.post(
            self.github_uri + '/login/oauth/access_token/',
            json=data,
            headers={'Accept': 'application/json'})
        return r.json()

    def get(self, resource, access_token):
        params = dict(access_token=access_token)
        r = requests.get(
            self.github_api_uri + resource,
            params=params,
            headers={'Accept': 'application/json'})
        return r.json()


class AuthCallBack(Resource):

    def get(self):
        code = request.args.get('code')
        github = GitHub()
        auth_response = github.authorize_access(code)
        access_token = auth_response.get('access_token')
        scope = auth_response.get('scope')
        if access_token is None:
            return {'error': 'login failed'}
        emails = github.get('/user/emails', access_token)
        for email in emails:
            if email['primary'] == True and email['verified'] == True:
                primary_email = email['email']
                break
        else:
            return {'error': 'No verified email'}
        user = User.query.filter_by(email=primary_email).first()
        if user is None:
            user = User(email=primary_email)
            db.session.add(user)
        user.github_access_token = access_token
        db.session.commit()

        session['user_id'] = user.id
        return {"message": "success!"}


class Auth(Resource):
    def get(self):
        if session.get('user_id', None) is None:
            return GitHub().authorize()
        else:
            return {'message': g.user.id}

    def delete(self):
        session.pop('user_id', None)
        return {'message': 'logged out'}


auth_api.add_resource(Auth, '/')
auth_api.add_resource(AuthCallBack, '/callback')
