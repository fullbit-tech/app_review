import time
from fabric.api import env, execute, run
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
        self.host = host
        self.access_token = access_token

    def _format_repo_auth(self, repo_url):
        return repo_url.replace(
            'https://',
            'https://{access_key}:x-oauth-basic@'.format(
                access_key=self.access_token, repo_url=repo_url))

    def wait_for_conn(self):
        self._wait_for_conn()

    def clone_repository(self, repo_url):
        execute(self._clone_repository,
                self._format_repo_auth(repo_url))

    def checkout_branch(self, branch):
        execute(self._checkout_branch, branch)

    def update_branch(self, branch):
        execute(self._update_branch, branch)

    def run_script(self, script):
        execute(self._run_script, script)

    def _wait_for_conn(self):
        try:
            time.sleep(20)
            run("pwd")
        except NetworkError:
            self._wait_for_conn()

    def _clone_repository(self, repo_url):
        run("sudo apt-get install git -y")
        run("sudo rm -rf /srv/app")
        run("sudo git clone {} /srv/app".format(repo_url))

    def _checkout_branch(self, branch):
        run("sudo git -C /srv/app fetch")
        run("sudo git -C /srv/app checkout {branch}".format(
            branch=branch))

    def _update_branch(self, branch):
        run("sudo git -C /srv/app reset --hard origin/{branch}".format(
            branch=branch))

    def _run_script(self, script):
        run(script)
