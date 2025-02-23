from dataclasses import dataclass
from git import Repo, exc
import os
from typing import List, Optional

def get_repo(path: Optional[str] = None) -> Optional[Repo]:
    """Returns a Git repository object for the given path, defaults to the current directory."""
    if not path:
        path = os.getcwd()
    try:
        return Repo(path, search_parent_directories=True)
    except exc.InvalidGitRepositoryError:
        print('InvalidGitRepositoryError')
        return None

@dataclass
class FileChange:
    path: str
    change_type: str
    content: str
    old_content: str = ""

def get_diff(repo: Repo, branch: Optional[str] = None, staged: bool = False) -> List[FileChange]:
    """Returns the diff of the repo, comparing with a branch or staging area."""
    changes = []
    
    if branch:
        diff_index = repo.head.commit.diff(repo.heads[branch], create_patch=True)
    elif staged:
        diff_index = repo.index.diff(repo.head.commit, create_patch=True)
    else:
        diff_index = repo.index.diff(None, create_patch=True)
        diff_index.extend(repo.index.diff(repo.head.commit, create_patch=True))
    
    for diff in diff_index:
        change_type = get_change_type(diff)
        content = diff.diff.decode('utf-8') if diff.diff else ""
        
        try:
            if branch:
                old_content = repo.git.show(f'{branch}:{diff.b_path}') if diff.b_path else ""
            else:
                old_content = repo.git.show(f'HEAD:{diff.b_path}') if diff.b_path else ""
        except:
            old_content = ""
            
        changes.append(FileChange(
            path=diff.b_path or diff.a_path,
            change_type=change_type,
            content=content,
            old_content=old_content
        ))
    
    return changes

def get_change_type(diff) -> str:
    if diff.new_file:
        return "added"
    elif diff.deleted_file:
        return "deleted"
    elif diff.renamed:
        return "renamed"
    return "modified"