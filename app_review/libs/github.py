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
        self.access_token = access_token
        self.scope = 'user:email,repo'
        self.user_agent = 'App-Review'

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
        if r.status_code != 200:
            raise GitHubException('Request Failed')
        return r.json()

    @req_access_token
    def _get(self, *args):
        r = requests.get(
            self.github_api_uri + '/'.join(args),
            headers={
                'Accept': 'application/json',
                'Authorization': 'token ' + self.access_token,
                'User-Agent': self.user_agent,
            })
        if r.status_code != 200:
            raise GitHubException('Request Failed')
        return r.json()

    @req_access_token
    def get_pull_request(self, owner, repo, number):
        """Returns pull request info"""
        return self._get('repos', owner, repo, 'pulls', number)


