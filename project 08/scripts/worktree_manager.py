"""Git worktree manager for Capstone Loop isolation."""

import subprocess
import json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class WorktreeInfo:
    path: str
    branch: str
    created_at: str


def _run_git(args: list[str], cwd: str | None = None, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a git command and return result."""
    return subprocess.run(
        ["git"] + args,
        capture_output=True, text=True, timeout=timeout, cwd=cwd,
    )


def get_repo_root(project_path: Path) -> Path:
    """Find the git repo root."""
    result = _run_git(["rev-parse", "--show-toplevel"], cwd=str(project_path))
    return Path(result.stdout.strip())


def create_worktree(
    project_path: Path,
    worktree_name: str = "worktree-capstone-audit",
) -> WorktreeInfo:
    """Create an isolated git worktree for the audit branch."""
    repo_root = get_repo_root(project_path)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"audit/capstone-{timestamp}"
    worktree_dir = repo_root.parent / worktree_name

    # Clean up stale worktree if it exists
    _run_git(["worktree", "remove", str(worktree_dir), "--force"], cwd=str(repo_root))

    # Create new worktree with new branch
    result = _run_git(
        ["worktree", "add", "-b", branch_name, str(worktree_dir)],
        cwd=str(repo_root), timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create worktree: {result.stderr}")

    return WorktreeInfo(
        path=str(worktree_dir),
        branch=branch_name,
        created_at=datetime.now().isoformat(),
    )


def push_branch(worktree_info: WorktreeInfo) -> bool:
    """Push audit branch to remote origin."""
    result = _run_git(
        ["push", "-u", "origin", worktree_info.branch],
        cwd=worktree_info.path, timeout=60,
    )
    return result.returncode == 0


def commit_changes(worktree_info: WorktreeInfo, message: str) -> bool:
    """Stage and commit all changes in the worktree."""
    _run_git(["add", "-A"], cwd=worktree_info.path)
    result = _run_git(
        ["commit", "-m", message],
        cwd=worktree_info.path,
    )
    return result.returncode == 0


def cleanup_worktree(worktree_info: WorktreeInfo) -> bool:
    """Remove the worktree and prune remote references."""
    repo_root = get_repo_root(Path(worktree_info.path))
    result = _run_git(
        ["worktree", "remove", worktree_info.path, "--force"],
        cwd=str(repo_root),
    )
    _run_git(["worktree", "prune"], cwd=str(repo_root))
    return result.returncode == 0


def list_worktrees(project_path: Path) -> list[dict]:
    """List all active worktrees."""
    repo_root = get_repo_root(project_path)
    result = _run_git(["worktree", "list", "--porcelain"], cwd=str(repo_root))
    worktrees = []
    current = {}
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("HEAD "):
            current["head"] = line.split(" ", 1)[1]
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1]
    if current:
        worktrees.append(current)
    return worktrees


if __name__ == "__main__":
    import sys
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    wt = create_worktree(path)
    print(json.dumps({"path": wt.path, "branch": wt.branch}, indent=2))
