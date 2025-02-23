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
    
    try:
        if branch:
            diff_index = repo.head.commit.diff(repo.heads[branch], create_patch=True)
        elif staged:
            diff_index = repo.index.diff(repo.head.commit, create_patch=True, R=True)
        else:
            diff_index = repo.index.diff(None, create_patch=True)
            staged_diff = repo.head.commit.diff(repo.index, create_patch=True)
            diff_index.extend(staged_diff)

        for diff in diff_index:
            change_type = get_change_type(diff)
            content = diff.diff.decode('utf-8') if diff.diff else ""
            
            try:
                if diff.new_file:
                    old_content = ""
                elif branch:
                    old_content = repo.git.show(f'{branch}:{diff.a_path}') if diff.a_path else ""
                else:
                    old_content = repo.git.show(f'HEAD:{diff.a_path}') if diff.a_path else ""
            except Exception as e:
                old_content = ""
                
            changes.append(FileChange(
                path=diff.b_path or diff.a_path,
                change_type=change_type,
                content=content,
                old_content=old_content
            ))
            
    except Exception as e:
        raise GitError(f"Failed to get diff: {str(e)}")
        
    return changes

def get_change_type(diff) -> str:
    if diff.new_file:
        return "added"
    elif diff.deleted_file:
        return "deleted"
    elif diff.renamed:
        return "renamed"
    return "modified"