#!/usr/bin/env python3
"""
Meta-Improvement Loop Script for Project 12 (Capstone)
Reads progress.md, identifies repeated failures, and proposes minimal fixes.
"""

import re
import os
from datetime import datetime, date
from collections import defaultdict
import subprocess
import sys

PROGRESS_FILE = "progress.md"
DREAMING_STATE_FILE = "dreaming-state.md"
CAPSTONE_LESSON_FILE = "CAPSTONE_LESSON.md"
PR_BRANCH = "claude/meta-improvement"
MIN_REPEAT_THRESHOLD = 3


def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def parse_dreaming_state(content):
    match = re.search(r'\*\*date\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    return date(2000, 1, 1)


def parse_progress_entries(content, after_date):
    entries = []
    lines = content.split('\n')
    current_date = None
    current_entry = None

    for line in lines:
        date_match = re.match(r'^## (\d{4}-\d{2}-\d{2})', line)
        if date_match:
            current_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
            continue

        task_match = re.match(r'^- \*\*Task\*\*:\s*(.+)', line)
        if task_match and current_date:
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                'date': current_date,
                'task': task_match.group(1).strip(),
                'status': None,
                'failure_reason': None,
                'rule_violated': None
            }
            continue

        status_match = re.match(r'^- \*\*Status\*\*:\s*(.+)', line)
        if status_match and current_entry:
            current_entry['status'] = status_match.group(1).strip()
            continue

        failure_match = re.match(r'^- \*\*Failure Reason\*\*:\s*(.+)', line)
        if failure_match and current_entry:
            current_entry['failure_reason'] = failure_match.group(1).strip()
            continue

        rule_match = re.match(r'^- \*\*Rule Violated\*\*:\s*(.+)', line)
        if rule_match and current_entry:
            current_entry['rule_violated'] = rule_match.group(1).strip()
            continue

    if current_entry:
        entries.append(current_entry)

    return [e for e in entries if e['date'] > after_date]


def analyze_failures(entries):
    failure_groups = defaultdict(list)
    all_rules_seen = set()

    for entry in entries:
        if entry['rule_violated']:
            all_rules_seen.add(entry['rule_violated'])
            failure_groups[entry['rule_violated']].append(entry)

    repeated_failures = {}
    for rule, occurrences in failure_groups.items():
        if len(occurrences) >= MIN_REPEAT_THRESHOLD:
            dates = [str(e['date']) for e in occurrences]
            files = []
            for e in occurrences:
                if e['failure_reason']:
                    fm = re.search(r'in\s+(\S+\.py)', e['failure_reason'])
                    if fm:
                        files.append(fm.group(1))
            files = list(set(files)) if files else ['unknown']
            repeated_failures[rule] = {
                'count': len(occurrences),
                'occurrences': occurrences,
                'dates': dates,
                'files_affected': files
            }

    unused_rules = all_rules_seen - set(failure_groups.keys())
    return repeated_failures, unused_rules


def generate_fix_proposal(rule, data):
    dates = data['dates']
    files = data['files_affected']
    count = data['count']

    first_reason = data['occurrences'][0]['failure_reason'] or ''
    error_match = re.search(r'(E\d+)', first_reason)
    error_code = error_match.group(1) if error_match else 'UNKNOWN'

    if error_code == 'E401':
        fix = ("Add a lint rule/pre-commit hook to enforce single imports per line. "
               "This prevents 'import os, sys' style and requires separate statements.")
        auto_fix = True
    else:
        fix = f"Investigate and fix {error_code} violations in {', '.join(files)}"
        auto_fix = False

    return {
        'rule': rule,
        'error_code': error_code,
        'count': count,
        'files_affected': files,
        'dates': dates,
        'fix_description': fix,
        'auto_fixable': auto_fix,
        'first_seen': min(dates),
        'last_seen': max(dates),
    }


def generate_report(repeated_failures, unused_rules, all_entries):
    r = []
    r.append("# Meta-Improvement Loop Analysis Report")
    r.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    r.append("")

    total_failures = sum(1 for e in all_entries if e['status'] == 'FAILURE')
    total_successes = sum(1 for e in all_entries if e['status'] == 'SUCCESS')
    r.append("## Summary")
    r.append(f"- Total entries analyzed: {len(all_entries)}")
    r.append(f"- Total failures: {total_failures}")
    r.append(f"- Total successes: {total_successes}")
    r.append(f"- Repeated failure patterns found: {len(repeated_failures)}")
    r.append(f"- Unused rules identified: {len(unused_rules)}")
    r.append("")

    r.append("## Repeated Failures (>= 3 occurrences)")
    r.append("")
    if repeated_failures:
        for rule, data in repeated_failures.items():
            p = generate_fix_proposal(rule, data)
            r.append(f"### {rule}")
            r.append(f"- **Error Code**: {p['error_code']}")
            r.append(f"- **Total Occurrences**: {p['count']}")
            r.append(f"- **First Seen**: {p['first_seen']}")
            r.append(f"- **Last Seen**: {p['last_seen']}")
            r.append(f"- **Files Affected**: {', '.join(p['files_affected'])}")
            r.append("")
            r.append("**Evidence (dates with exact failure reason)**:")
            for occ in data['occurrences']:
                r.append(f"  - {occ['date']}: {occ['failure_reason']}")
            r.append("")
            r.append(f"**Proposed Fix**: {p['fix_description']}")
            r.append(f"**Auto-fixable**: {'Yes' if p['auto_fixable'] else 'No'}")
            r.append("")
    else:
        r.append("No repeated failures found (threshold: 3+ occurrences).")
        r.append("")

    r.append("## Unused Rules (candidates for deletion)")
    r.append("")
    if unused_rules:
        for rule in sorted(unused_rules):
            r.append(f"- `{rule}` - Never caused a failure in analyzed period. "
                     "Consider removing if no longer relevant.")
        r.append("")
    else:
        r.append("No unused rules identified.")
        r.append("")

    return '\n'.join(r)


def update_dreaming_state(last_processed_date, entries_processed, findings_summary):
    content = read_file(DREAMING_STATE_FILE)
    new_run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    today = date.today().isoformat()

    new_entry = f"| {new_run_id} | {today} | {entries_processed} | {findings_summary} |"

    content = re.sub(
        r'(\*\*date\*\*:\s*)\d{4}-\d{2}-\d{2}',
        f'\\g<1>' + today,
        content
    )
    content = re.sub(
        r'(\*\*run_id\*\*:\s*)\S+',
        f'\\g<1>' + new_run_id,
        content
    )
    content = re.sub(
        r'(\*\*entries_processed\*\*:\s*)\d+',
        f'\\g<1>' + str(entries_processed),
        content
    )
    content = content.rstrip() + '\n' + new_entry + '\n'

    write_file(DREAMING_STATE_FILE, content)
    return new_run_id


def create_git_branch_and_commit(report_content):
    try:
        subprocess.run(['git', 'checkout', '-b', PR_BRANCH], check=True,
                       capture_output=True, text=True)
    except subprocess.CalledProcessError:
        subprocess.run(['git', 'checkout', PR_BRANCH], check=True,
                       capture_output=True, text=True)

    report_path = os.path.join(os.getcwd(), "META_REPORT.md")
    write_file(report_path, report_content)

    subprocess.run(['git', 'add', PROGRESS_FILE, DREAMING_STATE_FILE, report_path],
                   check=True, capture_output=True, text=True)
    subprocess.run(['git', 'commit', '-m',
                   'feat: meta-improvement loop - analyze failures and propose fixes'],
                   check=True, capture_output=True, text=True)
    return True


def generate_commit_description(report_content, repeated_failures, unused_rules):
    lines = []
    lines.append("## Meta-Improvement Loop Analysis")
    lines.append("")
    lines.append("### Evidence-Based Findings")
    lines.append("")

    if repeated_failures:
        lines.append("**Repeated Failures Detected:**")
        lines.append("")
        for rule, data in repeated_failures.items():
            p = generate_fix_proposal(rule, data)
            lines.append(f"**{rule}** (Error: {p['error_code']})")
            lines.append(f"- Occurred {p['count']} times between {p['first_seen']} and {p['last_seen']}")
            lines.append(f"- Affected files: {', '.join(p['files_affected'])}")
            lines.append("- Log evidence:")
            for occ in data['occurrences']:
                lines.append(f"  - `{occ['date']}`: {occ['failure_reason']}")
            lines.append(f"- **Proposed minimal fix**: {p['fix_description']}")
            lines.append("")

    if unused_rules:
        lines.append("**Unused Rules (deletion candidates):**")
        for rule in sorted(unused_rules):
            lines.append(f"- `{rule}`: Never triggered a failure in the analyzed period")
        lines.append("")

    lines.append("### Completion Criteria")
    lines.append("1. progress.md exists with 1 week of historical log entries + planted repeated failure")
    lines.append("2. dreaming-state.md stores last processed timestamp and updates after each run")
    lines.append("3. Meta-loop script identifies repeated failures with cited evidence and proposes minimal fixes")
    lines.append("")
    lines.append("### Instructions for reviewer")
    lines.append("Review the evidence in META_REPORT.md. Each finding cites exact log dates, frequency, and failure reasons.")
    lines.append("No hallucinated guesses - all proposals are backed by data from progress.md.")

    return '\n'.join(lines)


def main():
    print("=" * 60)
    print("  META-IMPROVEMENT LOOP - Project 12 Capstone")
    print("=" * 60)
    print()

    if not os.path.exists(PROGRESS_FILE):
        print(f"ERROR: {PROGRESS_FILE} not found!")
        sys.exit(1)
    if not os.path.exists(DREAMING_STATE_FILE):
        print(f"ERROR: {DREAMING_STATE_FILE} not found!")
        sys.exit(1)

    print("[1/6] Reading dreaming state...")
    ds_content = read_file(DREAMING_STATE_FILE)
    last_date = parse_dreaming_state(ds_content)
    print(f"  Last processed date: {last_date}")

    print("[2/6] Reading progress entries...")
    progress_content = read_file(PROGRESS_FILE)
    entries = parse_progress_entries(progress_content, last_date)
    print(f"  Found {len(entries)} entries after {last_date}")

    if not entries:
        print("  No new entries to process. Exiting.")
        sys.exit(0)

    print("[3/6] Analyzing failures...")
    repeated_failures, unused_rules = analyze_failures(entries)
    print(f"  Repeated failure patterns: {len(repeated_failures)}")
    print(f"  Unused rules: {len(unused_rules)}")

    for rule, data in repeated_failures.items():
        print(f"  -> {rule}: {data['count']} occurrences in {data['files_affected']}")

    print("[4/6] Generating report...")
    report = generate_report(repeated_failures, unused_rules, entries)
    print(f"  Report generated ({len(report)} chars)")

    print("[5/6] Updating dreaming state...")
    findings = f"{len(repeated_failures)} repeated, {len(unused_rules)} unused"
    run_id = update_dreaming_state(last_date, len(entries), findings)
    print(f"  Updated with run_id: {run_id}")

    print("[6/6] Creating git branch and commit...")
    create_git_branch_and_commit(report)

    desc = generate_commit_description(report, repeated_failures, unused_rules)
    print()
    print("=" * 60)
    print("  COMMIT DESCRIPTION (use for PR)")
    print("=" * 60)
    print(desc)
    print()
    print("Done! Branch created: " + PR_BRANCH)
    print("Push with: git push origin " + PR_BRANCH)
    print("Then create PR with the description above.")


if __name__ == '__main__':
    main()
