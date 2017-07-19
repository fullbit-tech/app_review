import requests
from flask import current_app, redirect


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
