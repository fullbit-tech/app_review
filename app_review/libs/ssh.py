import time
from fabric.api import env, execute, sudo
from fabric.exceptions import NetworkError
from flask import current_app


class SSH(object):
    """Provides an interface for running commands
       on remote hosts using SSH.
    """
    def __init__(self, host, access_token):
        env.key_filename = current_app.config['AWS_KEY_FILE']
        env.host_string = "{user}@{host}".format(
            user=current_app.config['AWS_HOST_USERNAME'], host=host)
        env.output_prefix = False
        self.host = host
        self.access_token = access_token

    def _format_repo_auth(self, repo_url):
        return repo_url.replace(
            'https://',
            'https://{access_key}:x-oauth-basic@'.format(
                access_key=self.access_token, repo_url=repo_url))

    def wait_for_conn(self):
        return self._wait_for_conn()

    def clone_repository(self, repo_url):
        return execute(self._clone_repository,
                       self._format_repo_auth(repo_url))['<local-only>']

    def checkout_branch(self, branch):
        return execute(self._checkout_branch, branch)['<local-only>']

    def update_branch(self, branch):
        return execute(self._update_branch, branch)['<local-only>']

    def run_script(self, script):
        return execute(self._run_script, script)['<local-only>']

    def _wait_for_conn(self):
        try:
            time.sleep(20)
            sudo("pwd")
        except NetworkError:
            self._wait_for_conn()

    def _clone_repository(self, repo_url):
        return [sudo("apt-get update -y"),
                sudo("apt-get install git -y"),
                sudo("rm -rf /srv/app"),
                sudo("git clone {} /srv/app".format(repo_url))]

    def _checkout_branch(self, branch):
        return [sudo("git -C /srv/app fetch"),
                sudo("git -C /srv/app checkout {branch}".format(
                    branch=branch))]

    def _update_branch(self, branch):
        return [sudo("git -C /srv/app reset --hard origin/{branch}".format(
                branch=branch))]

    def _run_script(self, script):
        return [sudo(script, warn_only=True)]
