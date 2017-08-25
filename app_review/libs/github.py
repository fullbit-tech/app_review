import hmac
import hashlib
import base64
import requests
from flask import current_app, redirect


class GitHubException(Exception):
    pass


def req_access_token(f):
    def wrapper(*args, **kwargs):
        if not args[0].access_token:
            raise GitHubException('Requires access token')
        return f(*args, **kwargs)
    return wrapper


class GitHub(object):
    def __init__(self, access_token=None, scope='user:email,repo'):
        self.github_uri = 'https://github.com/'
        self.github_api_uri = 'https://api.github.com/'
        self.client_id = current_app.config['GITHUB_CLIENT_ID']
        self.client_secret = current_app.config['GITHUB_CLIENT_SECRET']
        self.callback_url = current_app.config['APP_REVIEW_WEB_URL']
        self.signature_secret = current_app.config['GITHUB_SIGNATURE_SECRET']
        self.access_token = access_token
        self.scope = 'user:email,repo'
        self.user_agent = 'App-Review'

    def verify_signature(self, signature, body):
        dig = 'sha1=' + hmac.new(self.signature_secret,
                                 body, hashlib.sha1).hexdigest()
        return hmac.compoare(dig, signature)

    def authorize(self):
        return redirect((
            '{git_uri}login/oauth/authorize'
            '?scope={scope}&client_id={client_id}').format(
                git_uri=self.github_uri,
                scope=self.scope,
                client_id=self.client_id),
            code=302)

    def authorize_access(self, code, state):
        data = dict(client_id=self.client_id,
                    client_secret=self.client_secret,
                    code=code,
                    state=state)
        r = requests.post(
            self.github_uri + 'login/oauth/access_token/',
            json=data,
            headers={'Accept': 'application/json'})
        if r.status_code != requests.codes.ok:
            raise GitHubException('Request Failed')
        return r.json()

    @req_access_token
    def _get(self, *args, **kwargs):
        r = requests.get(
            self.github_api_uri + '/'.join(args),
            params=kwargs,
            headers={
                'Accept': 'application/json',
                'Authorization': 'token ' + self.access_token,
                'User-Agent': self.user_agent,
            })
        if r.status_code != requests.codes.ok:
            raise GitHubException('Request Failed')
        return r.json()

    @req_access_token
    def _post(self, *args, **kwargs):
        r = requests.post(
            self.github_api_uri + '/'.join(args),
            json=kwargs,
            headers={
                'Accept': 'application/json',
                'Authorization': 'token ' + self.access_token,
                'User-Agent': self.user_agent,
            })
        return r.json()
        if r.status_code != requests.codes.ok:
            raise GitHubException('Request Failed')
        return r.json()

    @req_access_token
    def _delete(self, *args):
        r = requests.delete(
            self.github_api_uri + '/'.join(args),
            headers={
                'Accept': 'application/json',
                'Authorization': 'token ' + self.access_token,
                'User-Agent': self.user_agent,
            })
        if r.status_code != requests.codes.ok:
            raise GitHubException('Request Failed')
        return r.json()

    @req_access_token
    def _create_comment(self, url, message):
        r = requests.post(
            url,
            json={"body": message},
            headers={
                'Accept': 'application/json',
                'Authorization': 'token ' + self.access_token,
                'User-Agent': self.user_agent,
            })
        return r.json()


    @req_access_token
    def get_pull_request(self, owner, repo, number):
        """Returns pull request info"""
        return self._get('repos', owner, repo, 'pulls', number)

    @req_access_token
    def get_pull_requests(self, owner, repo):
        """Returns associated organizations"""
        return self._get('repos', owner, repo, 'pulls', state="open")

    @req_access_token
    def get_repository(self, owner, repo):
        """Returns repository info"""
        return self._get('repos', owner, repo)

    @req_access_token
    def create_comment(self, url, message):
        """Returns repository info"""
        return self._create_comment(url, message)

    @req_access_token
    def get_user(self):
        """Returns authenticated user info"""
        return self._get('user')

    @req_access_token
    def create_pull_request_hook(self, owner, repo):
        data = {
            'name': 'web',
            'active': True,
            'events': ['pull_request'],
            'config': {
                'url': self.callback_url + '/hook/github/pull-request',
                'content_type': 'json',
                'secret': self.signature_secret,
            }
        }
        return self._post('repos', owner, repo, 'hooks', **data)


    @req_access_token
    def delete_pull_request_hook(self, owner, repo, hook_id):
        return self._delete('repos', owner, repo, 'hooks', str(hook_id))
