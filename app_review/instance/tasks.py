from app_review.extensions import celery
from app_review.libs.ssh import SSH
from app_review.libs.github import GitHub, GitHubException
from app_review.instance.models import PullRequestInstance


@celery.task
def pull_synchronize(instance_id):
    instance = PullRequestInstance.query.filter_by(id=instance_id).first()
    repo_link = instance.repository_link
    gh = GitHub(access_token=repo_link.user.github_access_token)
    try:
        pull_request = gh.get_pull_request(
            repo_link.owner,
            repo_link.repository,
            instance.github_pull_number)
    except GitHubException:
        return
    ssh = SSH(instance.instance_url, repo_link.user.github_access_token)
    try:
        ssh.wait_for_conn()
        ssh.clone_repository(pull_request['base']['repo']['clone_url'])
        ssh.checkout_branch(pull_request['head']['ref'])
    except SystemExit:
        return # TODO - Add some logging
    instance.stop()
    instance.start()
