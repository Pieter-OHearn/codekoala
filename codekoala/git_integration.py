from dataclasses import dataclass
import os
from typing import Iterable, List, Optional

from git import Repo, exc


class GitIntegrationError(RuntimeError):
    """Raised when git diff operations fail."""


def get_repo(path: Optional[str] = None) -> Optional[Repo]:
    """Return a Git repository object for the given path, defaults to the current directory."""
    if not path:
        path = os.getcwd()
    try:
        return Repo(path, search_parent_directories=True)
    except exc.InvalidGitRepositoryError:
        print("InvalidGitRepositoryError")
        return None


@dataclass
class FileChange:
    path: str
    change_type: str
    content: str
    old_content: str = ""


def get_diff(repo: Repo, branch: Optional[str] = None, staged: bool = False) -> List[FileChange]:
    """Return the diff of the repo, comparing with a branch or staging area."""
    changes: List[FileChange] = []

    try:
        if branch:
            target_commit = repo.commit(branch)
            head_commit = repo.head.commit if repo.head.is_valid() else None
            if head_commit:
                diff_index = head_commit.diff(target_commit, create_patch=True)
            else:
                diff_index = target_commit.diff(None, create_patch=True)
        elif staged:
            if repo.head.is_valid():
                diff_index = repo.index.diff("HEAD", create_patch=True)
            else:
                diff_index = repo.index.diff(None, create_patch=True)
        else:
            diff_index = list(repo.index.diff(None, create_patch=True))
            if repo.head.is_valid():
                staged_diff = repo.index.diff("HEAD", create_patch=True)
                diff_index.extend(staged_diff)

        for diff in _iter_diffs(diff_index):
            change_type = _get_change_type(diff)
            content = diff.diff.decode("utf-8") if diff.diff else ""

            try:
                if diff.new_file:
                    old_content = ""
                elif branch:
                    old_content = repo.git.show(f"{branch}:{diff.a_path}") if diff.a_path else ""
                else:
                    old_content = repo.git.show(f"HEAD:{diff.a_path}") if diff.a_path else ""
            except Exception:
                old_content = ""

            changes.append(
                FileChange(
                    path=diff.b_path or diff.a_path,
                    change_type=change_type,
                    content=content,
                    old_content=old_content,
                )
            )

    except exc.GitCommandError as error:
        stderr = getattr(error, "stderr", "") or getattr(error, "stdout", "") or str(error)
        raise GitIntegrationError(f"Failed to get diff: {stderr.strip()}") from error
    except Exception as error:
        raise GitIntegrationError(f"Failed to get diff: {str(error)}") from error

    return changes


def _iter_diffs(diff_index: Iterable) -> List:
    if isinstance(diff_index, list):
        return diff_index
    return list(diff_index)


def _get_change_type(diff) -> str:
    if diff.new_file:
        return "added"
    if diff.deleted_file:
        return "deleted"
    if diff.renamed:
        return "renamed"
    return "modified"
