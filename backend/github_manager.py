import os
import json
from github import Github, GithubException
from github import Auth

def save_to_github(data, repo_name, file_path, commit_message, branch="main"):
    """
    Save or update a JSON file in a GitHub repository.
    Returns a dict with status and URL or error message.
    """
    token = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        return {"success": False, "error": "GITHUB_TOKEN environment variable not set"}

    auth = Auth.Token(token)
    g = Github(auth=auth)

    try:
        repo = g.get_repo(repo_name)
        content_str = json.dumps(data, indent=4)

        try:
            # Try to get existing file
            contents = repo.get_contents(file_path, ref=branch)
            # Update existing file
            update_result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=content_str,
                sha=contents.sha,
                branch=branch
            )
            return {
                "success": True,
                "action": "updated",
                "url": update_result['content'].html_url
            }
        except GithubException as e:
            if e.status == 404:
                # File not found – create new
                create_result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content_str,
                    branch=branch
                )
                return {
                    "success": True,
                    "action": "created",
                    "url": create_result['content'].html_url
                }
            else:
                raise e
    except GithubException as e:
        return {"success": False, "error": f"GitHub API error: {e.data.get('message', str(e))}"}
    finally:
        g.close()