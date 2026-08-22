#!/usr/bin/env python3
"""Capstone Loop Orchestrator: Dependency & Lint Audit with Maker-Checker."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audit_chore import run_full_audit, identify_safe_bumps
from worktree_manager import create_worktree, commit_changes, push_branch, cleanup_worktree
from maker_checker import maker_checker_once
from pr_creator import create_audit_pr
from logger import log_loop_entry, log_human_intervention, get_last_beat_number
from budget_guard import BudgetState


PROJECT_PATH = Path(__file__).parent.parent
PROGRESS_FILE = PROJECT_PATH / "progress.md"
MAX_RETRIES = 2
TOKEN_ESTIMATE_PER_OP = {
    "audit": 5000,
    "maker_lint": 4000,
    "maker_bumps": 3000,
    "checker": 3000,
    "pr_create": 2000,
    "logging": 500,
}


def run_capstone_loop() -> dict:
    """Execute the full Capstone Loop and return status."""
    beat = get_last_beat_number(PROGRESS_FILE) + 1
    budget = BudgetState(max_retries=MAX_RETRIES, token_threshold=50000)
    worktree_info = None
    status = "RUNNING"

    try:
        # Phase 1: Create isolated worktree
        print(f"[Beat #{beat}] Creating worktree...")
        worktree_info = create_worktree(PROJECT_PATH)
        worktree_project = Path(worktree_info.path) / "project 8"
        print(f"  Worktree: {worktree_info.path}")
        print(f"  Branch: {worktree_info.branch}")
        print(f"  Project path: {worktree_project}")

        # Phase 2: Run audit
        total_tokens = TOKEN_ESTIMATE_PER_OP["audit"]
        if not budget.check_budget(total_tokens):
            raise RuntimeError("BUDGET_EXCEEDED")
        budget.record_usage(TOKEN_ESTIMATE_PER_OP["audit"], "audit")

        print("  Running audit...")
        audit = run_full_audit(worktree_project)
        audit_dict = audit.to_dict()
        print(f"  Lint issues: {audit_dict['lint_issues']}")
        print(f"  Outdated: {audit_dict['outdated_packages']}")
        print(f"  Vulnerabilities: {audit_dict['vulnerabilities']}")

        if not audit.has_issues:
            print("  No issues found. Nothing to fix.")
            status = "PASSED_NO_CHANGES"
            log_loop_entry(
                PROGRESS_FILE, beat, "Lint Sweep & Dependency Audit",
                worktree_info.branch,
                verdict="PASSED", status=status, tokens_spent=budget.tokens_used,
            )
            return {"status": status, "beat": beat}

        # Phase 3: Maker-Checker loop
        print("  Running Maker-Checker loop...")
        for attempt in range(MAX_RETRIES + 1):
            maker_cost = TOKEN_ESTIMATE_PER_OP["maker_lint"] + TOKEN_ESTIMATE_PER_OP["maker_bumps"]
            checker_cost = TOKEN_ESTIMATE_PER_OP["checker"]
            needed = maker_cost + checker_cost
            print(f"    Attempt {attempt+1}: tokens_used={budget.tokens_used}, needed={needed}, threshold={budget.token_threshold}")
            if not budget.check_budget(needed):
                raise RuntimeError("BUDGET_EXCEEDED")
            budget.record_usage(needed, f"maker_checker_attempt_{attempt + 1}")
            budget.increment_retry()
            print(f"    After: tokens_used={budget.tokens_used}, retry_count={budget.retry_count}")

            maker_result, checker_result = maker_checker_once(
                str(worktree_project), audit,
            )

            if checker_result.passed:
                print(f"  Maker-Checker PASSED on attempt {attempt + 1}")
                break
            print(f"  Attempt {attempt + 1} failed ({checker_result.failures} test failures)")
            if attempt == MAX_RETRIES:
                print("  Max retries reached.")
                status = "FAILED_TEST_FAILURES"
                break

        # Phase 4: Commit and push
        if checker_result.passed and maker_result.applied:
            commit_msg = f"chore(deps): audit sweep - {len(maker_result.applied)} fixes applied"
            commit_changes(worktree_info, commit_msg)
            push_branch(worktree_info)

            # Phase 5: Create PR
            pr_cost = TOKEN_ESTIMATE_PER_OP["pr_create"]
            if not budget.check_budget(pr_cost):
                raise RuntimeError("BUDGET_EXCEEDED")
            budget.record_usage(pr_cost, "pr_create")

            print("  Creating PR...")
            pr_result = create_audit_pr(
                worktree_info.path,
                worktree_info.branch,
                audit_dict,
                maker_result.applied,
                checker_result.passed,
            )
            pr_url = pr_result.pr_url or "Failed to create PR"
            status = "PASSED" if pr_result.success else "PR_FAILED"
        else:
            pr_url = None
            if not checker_result.passed:
                status = "FAILED_TEST_FAILURES"

        # Phase 6: Log results
        budget.record_usage(TOKEN_ESTIMATE_PER_OP["logging"], "logging")
        log_loop_entry(
            PROGRESS_FILE, beat, "Lint Sweep & Dependency Audit",
            worktree_info.branch,
            vulnerabilities=audit_dict["vulnerabilities"],
            lint_issues=audit_dict["lint_issues"],
            deps_bumped=maker_result.applied,
            verdict="PASSED" if checker_result.passed else "FAILED",
            pr_url=pr_url,
            tokens_spent=budget.tokens_used,
            status=status,
        )

        return {
            "status": status,
            "beat": beat,
            "worktree": worktree_info.branch,
            "audit": audit_dict,
            "maker": maker_result.applied,
            "checker_passed": checker_result.passed,
            "pr_url": pr_url,
            "budget": budget.to_dict(),
        }

    except RuntimeError as e:
        if "BUDGET_EXCEEDED" in str(e):
            status = "NEEDS HUMAN INTERVENTION"
            reason = f"Token budget exceeded ({budget.tokens_used}/{budget.token_threshold}). Max retries: {budget.retry_count}/{budget.max_retries}."
            log_human_intervention(PROGRESS_FILE, reason, beat)
            print(f"\n!!! NEEDS HUMAN INTERVENTION !!!")
            print(f"    {reason}")
        else:
            status = "ERROR"
            log_loop_entry(
                PROGRESS_FILE, beat, "Lint Sweep & Dependency Audit",
                worktree_info.branch if worktree_info else "N/A",
                status=f"ERROR: {e}", tokens_spent=budget.tokens_used,
            )
        return {"status": status, "beat": beat, "error": str(e)}

    finally:
        if worktree_info:
            print("  Cleaning up worktree...")
            cleanup_worktree(worktree_info)


def main():
    result = run_capstone_loop()
    print(f"\n{'='*50}")
    print(f"Capstone Loop Result: {result['status']}")
    print(f"Beat: #{result['beat']}")
    if "budget" in result:
        print(f"Tokens: {result['budget']['tokens_used']}")
        print(f"Retries: {result['budget']['retry_count']}")
    if "error" in result:
        print(f"Error: {result['error']}")
    print(f"{'='*50}")
    return 0 if result["status"] in ("PASSED", "PASSED_NO_CHANGES") else 1


if __name__ == "__main__":
    sys.exit(main())
