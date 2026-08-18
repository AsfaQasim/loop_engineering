"""Progress Logger: Append timestamped entries to progress.md."""

from datetime import datetime
from pathlib import Path
from typing import Optional


def log_loop_entry(
    progress_file: Path,
    beat_number: int,
    chore: str,
    worktree: str,
    vulnerabilities: int = 0,
    lint_issues: int = 0,
    deps_bumped: list[str] | None = None,
    verdict: str = "PENDING",
    pr_url: Optional[str] = None,
    tokens_spent: int = 0,
    status: str = "RUNNING",
    extra: dict | None = None,
) -> str:
    """Append a loop entry to progress.md and return the formatted string."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    deps_str = ", ".join(deps_bumped) if deps_bumped else "None"
    cost_estimate = f"~{tokens_spent:,} Tokens (${tokens_spent * 0.000004:.2f})"

    entry = f"""
## [{timestamp}] - Capstone Loop Beat #{beat_number}
- **Chore:** {chore}
- **Worktree:** {worktree}
- **Vulnerabilities Found:** {vulnerabilities}
- **Lint Issues Found:** {lint_issues}
- **Dependencies Bumped:** {deps_str}
- **Maker-Checker Verdict:** {verdict}
- **PR Created:** {pr_url or "None"}
- **Budget Spent:** {cost_estimate}
- **Status:** {status}
"""
    if extra:
        for k, v in extra.items():
            entry += f"- **{k}:** {v}\n"

    with open(progress_file, "a") as f:
        f.write(entry + "\n")

    return entry


def log_human_intervention(progress_file: Path, reason: str, beat_number: int) -> str:
    """Log a hard-stop human intervention entry."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"""
## [{timestamp}] - NEEDS HUMAN INTERVENTION (Beat #{beat_number})
- **Reason:** {reason}
- **Action Required:** Manual review and intervention needed
"""
    with open(progress_file, "a") as f:
        f.write(entry + "\n")
    return entry


def get_last_beat_number(progress_file: Path) -> int:
    """Parse progress.md to find the latest beat number."""
    if not progress_file.exists():
        return 0
    content = progress_file.read_text()
    import re
    matches = re.findall(r"Beat #(\d+)", content)
    if matches:
        return max(int(m) for m in matches)
    return 0


if __name__ == "__main__":
    from sys import argv
    p = Path(argv[1]) if len(argv) > 1 else Path("progress.md")
    num = get_last_beat_number(p)
    print(f"Last beat number: {num}")
