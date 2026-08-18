Project 7: Observability, Cost Math & Failure Handling
Production-grade monitoring, token economics estimation, and graceful sabotage escalation for unattended AI
agent loops.

Project Overview
When running autonomous AI developer agents unattended (overnight or on scheduled intervals), two primary risks arise:
uncontrolled token cost inflation and silent execution hanging. Project 7 establishes production observability, token
cost forecasting, and graceful error escalation mechanisms to ensure agents fail predictably and informatively without
wasting API budget.
Core Concepts Handled
1. Token Economics & Cost Calculation (Concept 13)
Every beat in an agent loop consumes input context (read) and writes outputs (write). Establishing a monthly budget
calculation prevents runaway API expenditure prior to background deployment.

Monthly Cadence = 24 runs/day × 30 days = 720 runs/month (1-Hour Interval)

Metric Tokens / Beat Cost / 1M Tokens Cost / Beat Monthly Total (720 Beats)
Input Tokens (Read) 15,000 $3.00 $0.0450 $32.40
Output Tokens (Write) 1,000 $15.00 $0.0150 $10.80
Total Estimated Cost 16,000 — $0.0600 ~$43.20 / Month
2. Sabotage Testing & Escalation Circuit (Concept 14)
To verify reliability, the system is subjected to a Sabotage Test by pointing the reviewer loop toward a non-existent file
( missing_file.py ). Rather than crashing silently or entering an unhandled infinite loop, the script executes controlled
retries and safely escalates.
Max Retry Threshold: 3 attempts
Exit Code: 1 (Controlled Process Termination)
Escalation Verdict: NEEDS HUMAN INTERVENTION
3. Spine-Only Diagnosis (Observability)
Engineers should not need to replay or re-execute agent sessions to diagnose overnight failures. All critical telemetry is
logged to progress.md (The Spine) for instant 5-second diagnostics.
Quick Start & Execution
Run the sabotage test via OpenCode CLI to verify retry logic and spine logging:
opencode run "Set up Project 7 Observability & Failure Handling:
1. Update reviewer script to target a non-existent file 'missing_file.py'.
2. Implement retry logic: attempt access up to 3 times.
•
•
•

Page 1 of 2

3. Upon failure, write an entry to 'progress.md' with timestamp, error reason, and explicit
status 'NEEDS HUMAN INTERVENTION'.
4. Exit with code 1 without unhandled crashes.
5. Run script once to record the failure log."

Diagnostic Log Specification (progress.md)
Upon controlled failure, the agent writes the following diagnostic block directly into progress.md :
## [2026-08-18 20:27:00 PKT] - EXECUTION FAILED
- Status: FAILED
- Retry Count: 3/3
- Error: Target file 'missing_file.py' not found.
- Verdict: NEEDS HUMAN INTERVENTION

Definition of Done
Project 7 Completion Checklist
Predictable Monthly Cost: Cost budget verified at ~$43.20/month for a 1-hour cadence.
No Silent Crashes: System gracefully handles unrecoverable states and exits with code 1.
Spine Telemetry: Root cause and timestamp identified purely via progress.md without session replay.