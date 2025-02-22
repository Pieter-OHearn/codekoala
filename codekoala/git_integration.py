import git
import os
from typing import Optional

def get_repo(path: Optional[str] = None) -> Optional[git.Repo]:
    """Returns a Git repository object for the given path, defaults to the current directory."""
    if not path:
        path = os.getcwd()
    try:
        return git.Repo(path, search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        print('InvalidGitRepositoryError')
        return None

def get_diff(repo: git.Repo, branch: Optional[str] = None, staged: bool = False) -> str:
    """Returns the diff of the repo, comparing with a branch or staging area."""
    if staged:
        return repo.git.diff('--cached', branch) if branch else repo.git.diff('--cached')
    else:
        return repo.git.diff(branch) if branch else repo.git.diff()
