"""Audit Chore: Lint sweep + dependency audit for Python projects."""

import subprocess
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class LintIssue:
    file: str
    line: int
    code: str
    message: str
    fixable: bool = False


@dataclass
class OutdatedPackage:
    name: str
    current: str
    latest: str
    type: str  # "major", "minor", "patch"


@dataclass
class AuditResult:
    lint_issues: list[LintIssue] = field(default_factory=list)
    outdated_packages: list[OutdatedPackage] = field(default_factory=list)
    vulnerabilities: list[dict] = field(default_factory=list)
    auto_fixable: int = 0
    manual_review: int = 0

    @property
    def has_issues(self) -> bool:
        return bool(self.lint_issues or self.outdated_packages or self.vulnerabilities)

    def to_dict(self) -> dict:
        return {
            "lint_issues": len(self.lint_issues),
            "outdated_packages": len(self.outdated_packages),
            "vulnerabilities": len(self.vulnerabilities),
            "auto_fixable": self.auto_fixable,
            "manual_review": self.manual_review,
        }


def run_ruff_check(project_path: Path) -> list[LintIssue]:
    """Run ruff linter and parse output."""
    issues = []
    try:
        result = subprocess.run(
            ["python", "-m", "ruff", "check", "--output-format=json", str(project_path / "src")],
            capture_output=True, text=True, timeout=60,
        )
        if result.stdout.strip():
            data = json.loads(result.stdout)
            for item in data:
                fix_info = item.get("fix") or {}
                issues.append(LintIssue(
                    file=item.get("filename", ""),
                    line=item.get("location", {}).get("row", 0),
                    code=item.get("code", ""),
                    message=item.get("message", ""),
                    fixable=fix_info.get("applicability", "") == "safe",
                ))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return issues


def run_ruff_format_check(project_path: Path) -> list[LintIssue]:
    """Check formatting issues via ruff format --check."""
    issues = []
    try:
        result = subprocess.run(
            ["python", "-m", "ruff", "format", "--check", "--diff", str(project_path / "src")],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            lines = result.stdout.splitlines()
            current_file = ""
            for line in lines:
                if line.startswith("---") or line.startswith("+++"):
                    parts = line.split()
                    if len(parts) >= 2:
                        current_file = parts[1].lstrip("+").lstrip("-")
                elif line.startswith("@@"):
                    match = re.search(r"\+(\d+)", line)
                    if match and current_file:
                        issues.append(LintIssue(
                            file=current_file,
                            line=int(match.group(1)),
                            code="FORMAT",
                            message="Formatting mismatch (ruff format)",
                            fixable=True,
                        ))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return issues


def check_outdated_packages(project_path: Path) -> list[OutdatedPackage]:
    """Check for outdated Python packages."""
    outdated = []
    try:
        result = subprocess.run(
            ["python", "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.stdout.strip():
            data = json.loads(result.stdout)
            for pkg in data:
                name = pkg.get("name", "")
                current = pkg.get("version", "")
                latest = pkg.get("latest_version", "")
                if name and current and latest:
                    pkg_type = "patch"
                    cur_parts = current.split(".")
                    lat_parts = latest.split(".")
                    if len(cur_parts) >= 1 and len(lat_parts) >= 1:
                        if cur_parts[0] != lat_parts[0]:
                            pkg_type = "major"
                        elif len(cur_parts) > 1 and len(lat_parts) > 1 and cur_parts[1] != lat_parts[1]:
                            pkg_type = "minor"
                    outdated.append(OutdatedPackage(
                        name=name, current=current, latest=latest, type=pkg_type,
                    ))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return outdated


def check_vulnerabilities(project_path: Path) -> list[dict]:
    """Run pip-audit for known vulnerabilities."""
    vulns = []
    try:
        req_file = project_path / "requirements.txt"
        cmd = ["python", "-m", "pip_audit", "--format=json"]
        if req_file.exists():
            cmd.extend(["-r", str(req_file)])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            # pip-audit returns a list of package dicts
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("vulns"):
                        for v in item["vulns"]:
                            vulns.append({
                                "package": item.get("name", ""),
                                "version": item.get("version", ""),
                                "vuln_id": v.get("id", ""),
                                "fix_versions": v.get("fix_versions", []),
                            })
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError, Exception):
        pass
    return vulns


def identify_safe_bumps(outdated: list[OutdatedPackage]) -> list[OutdatedPackage]:
    """Filter to only patch-level bumps (safe to auto-apply)."""
    return [p for p in outdated if p.type == "patch"]


def run_full_audit(project_path: Path) -> AuditResult:
    """Execute complete audit and return structured result."""
    lint_issues = run_ruff_check(project_path)
    format_issues = run_ruff_format_check(project_path)
    all_lint = lint_issues + format_issues
    outdated = check_outdated_packages(project_path)
    vulns = check_vulnerabilities(project_path)
    safe_bumps = identify_safe_bumps(outdated)

    return AuditResult(
        lint_issues=all_lint,
        outdated_packages=outdated,
        vulnerabilities=vulns,
        auto_fixable=len([i for i in all_lint if i.fixable]) + len(safe_bumps),
        manual_review=len([i for i in all_lint if not i.fixable]) + len(outdated) - len(safe_bumps),
    )


if __name__ == "__main__":
    import sys
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    result = run_full_audit(path)
    print(json.dumps(result.to_dict(), indent=2))
