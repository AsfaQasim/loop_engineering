"""Maker-Checker loop: Maker applies fixes, Checker validates with tests."""

import subprocess
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from audit_chore import AuditResult, OutdatedPackage, LintIssue


@dataclass
class MakerResult:
    applied: list[str]
    failed: list[str]
    commit_hash: Optional[str] = None


@dataclass
class CheckerResult:
    passed: bool
    tests_run: int
    failures: int
    output: str


def _run(cmd: list[str], cwd: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)


def maker_apply_lint_fixes(worktree_path: str, audit: AuditResult) -> MakerResult:
    """Auto-fix lint issues using ruff."""
    applied, failed = [], []
    fixable = [i for i in audit.lint_issues if i.fixable and i.code == "FORMAT"]
    if fixable:
        result = _run(
            ["python", "-m", "ruff", "format", "src/"],
            cwd=worktree_path,
        )
        if result.returncode == 0:
            applied.append(f"Formatted {len(fixable)} files with ruff format")
        else:
            failed.append(f"ruff format failed: {result.stderr[:200]}")

    ruff_fixable = [i for i in audit.lint_issues if i.fixable and i.code != "FORMAT"]
    if ruff_fixable:
        result = _run(
            ["python", "-m", "ruff", "check", "--fix", "src/"],
            cwd=worktree_path,
        )
        if result.returncode == 0:
            applied.append(f"Auto-fixed {len(ruff_fixable)} lint issues with ruff --fix")
        else:
            failed.append(f"ruff --fix failed: {result.stderr[:200]}")

    return MakerResult(applied=applied, failed=failed)


def maker_apply_version_bumps(worktree_path: str, safe_bumps: list[OutdatedPackage]) -> MakerResult:
    """Bump safe patch-level dependencies in requirements.txt."""
    applied, failed = [], []
    req_file = Path(worktree_path) / "requirements.txt"
    if not req_file.exists() or not safe_bumps:
        return MakerResult(applied=[], failed=[])

    content = req_file.read_text()
    for pkg in safe_bumps:
        pattern = re.compile(rf"^{re.escape(pkg.name)}>=[\d.]+", re.MULTILINE)
        replacement = f"{pkg.name}>={pkg.latest}"
        new_content, count = pattern.subn(replacement, content)
        if count > 0:
            content = new_content
            applied.append(f"{pkg.name}: {pkg.current} -> {pkg.latest}")
        else:
            failed.append(f"Could not bump {pkg.name}")

    req_file.write_text(content)
    return MakerResult(applied=applied, failed=failed)


def checker_run_tests(worktree_path: str) -> CheckerResult:
    """Run pytest and report results."""
    result = _run(
        ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=worktree_path, timeout=120,
    )
    output = result.stdout + "\n" + result.stderr
    passed = result.returncode == 0
    tests_run = 0
    failures = 0

    for line in output.splitlines():
        m = re.search(r"(\d+) passed", line)
        if m:
            tests_run += int(m.group(1))
        m = re.search(r"(\d+) failed", line)
        if m:
            failures += int(m.group(1))

    return CheckerResult(
        passed=passed,
        tests_run=tests_run,
        failures=failures,
        output=output[-2000:],
    )


def maker_checker_once(
    worktree_path: str,
    audit: AuditResult,
) -> tuple[MakerResult, CheckerResult]:
    """Run one iteration of Maker-Checker."""
    maker_lint = maker_apply_lint_fixes(worktree_path, audit)
    safe_bumps = [p for p in audit.outdated_packages if p.type == "patch"]
    maker_bumps = maker_apply_version_bumps(worktree_path, safe_bumps)

    combined = MakerResult(
        applied=maker_lint.applied + maker_bumps.applied,
        failed=maker_lint.failed + maker_bumps.failed,
    )

    checker = checker_run_tests(worktree_path)
    return combined, checker
