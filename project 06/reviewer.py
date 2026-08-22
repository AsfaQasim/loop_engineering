#!/usr/bin/env python3
"""PR Code Reviewer - checks for common bugs in Python code changes."""

import subprocess
import re
import sys


def get_diff():
    """Get the git diff for the current PR."""
    result = subprocess.run(
        ["git", "diff", "origin/master...HEAD"],
        capture_output=True, text=True
    )
    return result.stdout


def check_off_by_one(diff):
    """Check for potential off-by-one errors."""
    issues = []
    lines = diff.split("\n")
    for i, line in enumerate(lines):
        if not line.startswith("+") or line.startswith("+++"):
            continue
        code = line[1:]
        # Check for range() with potential off-by-one
        match = re.search(r'range\((\w+),\s*(\w+)\)', code)
        if match:
            issues.append(f"  - `range({match.group(1)}, {match.group(2)})`: Verify boundary - may miss last element")
        # Check for len() comparisons that might be off
        match = re.search(r'(\w+)\s*(<|<=|>|>=)\s*len\((\w+)\)', code)
        if match:
            issues.append(f"  - `{match.group(0)}`: Double-check index bounds")
        # Check for list indexing near boundaries
        match = re.search(r'\[(\w+)\[-1\]\]', code)
        if match:
            issues.append(f"  - `{match.group(0)}`: Verify list is non-empty before accessing index -1")
    return issues


def check_none_handling(diff):
    """Check for missing None checks."""
    issues = []
    lines = diff.split("\n")
    for line in lines:
        if not line.startswith("+") or line.startswith("+++"):
            continue
        code = line[1:]
        if re.search(r'\.get\([^)]+\)\[', code):
            issues.append(f"  - `{code.strip()}`: `.get()` may return None - check before indexing")
    return issues


def check_bare_except(diff):
    """Check for bare except clauses."""
    issues = []
    lines = diff.split("\n")
    for line in lines:
        if not line.startswith("+") or line.startswith("+++"):
            continue
        code = line[1:]
        if re.search(r'except\s*:', code):
            issues.append(f"  - `{code.strip()}`: Bare except catches all exceptions including KeyboardInterrupt")
    return issues


def check_mutable_default(diff):
    """Check for mutable default arguments."""
    issues = []
    lines = diff.split("\n")
    for line in lines:
        if not line.startswith("+") or line.startswith("+++"):
            continue
        code = line[1:]
        if re.search(r'def\s+\w+\([^)]*=\s*(\[\]|\{\}|set\(\))', code):
            issues.append(f"  - `{code.strip()}`: Mutable default argument - use None instead")
    return issues


def review():
    """Run all checks and output results."""
    diff = get_diff()
    if not diff:
        print("No changes detected.")
        sys.exit(0)

    all_issues = []

    checks = [
        ("Off-by-one / Boundary Errors", check_off_by_one),
        ("None Handling", check_none_handling),
        ("Bare Except Clauses", check_bare_except),
        ("Mutable Default Arguments", check_mutable_default),
    ]

    for name, check_fn in checks:
        issues = check_fn(diff)
        if issues:
            all_issues.append(f"### {name}\n" + "\n".join(issues))

    if all_issues:
        print("## OpenCode PR Review\n")
        print("Found potential issues:\n")
        print("\n\n".join(all_issues))
        print("\n---")
        print("*Reviewed by OpenCode Event-Driven PR Reviewer*")
    else:
        print("## OpenCode PR Review\n")
        print("No issues found. Code looks good!")
        print("\n---")
        print("*Reviewed by OpenCode Event-Driven PR Reviewer*")


if __name__ == "__main__":
    review()
