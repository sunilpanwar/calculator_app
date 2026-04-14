import os
import json
from github import Github, GithubException
from github import Auth

def save_to_github(data, repo_name, file_path, commit_message, branch="develop"):
    token = os.environ.get("PY_GITHUB_TOKEN")
    if not token:
        return {"success": False, "error": "GITHUB_TOKEN environment variable not set"}

    auth = Auth.Token(token)
    g = Github(auth=auth)

    try:
        repo = g.get_repo(repo_name)
        content_str = json.dumps(data, indent=4)

        try:
            contents = repo.get_contents(file_path, ref=branch)
            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=content_str,
                sha=contents.sha,
                branch=branch
            )
            return {
                "success": True,
                "action": "updated",
                "url": result['content'].html_url
            }
        except GithubException as e:
            if e.status == 404:
                # File not found – create new
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content_str,
                    branch=branch
                )
                return {
                    "success": True,
                    "action": "created",
                    "url": result['content'].html_url
                }
            else:
                # Re-raise to be caught by outer except
                raise e
    except GithubException as e:
        # Extract detailed error message from GitHub response
        error_msg = e.data.get('message', str(e))
        # Common 403 details
        if e.status == 403:
            error_msg += " — Check token permissions (needs 'repo' scope) and repository access."
        return {"success": False, "error": f"GitHub API error (status {e.status}): {error_msg}"}
    finally:
        g.close()