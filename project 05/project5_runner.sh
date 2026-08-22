#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="workflow_logs"
mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR/summary.log"

echo "=== STARTING PROJECT 5 PARALLEL WORKFLOW ==="

# Run each bug check in parallel
(python reviewer.py > "$LOG_DIR/bug1.log" 2>&1 && echo "issue-1: PASS" >> "$LOG_DIR/summary.log" || echo "issue-1: FAIL" >> "$LOG_DIR/summary.log") &
(python reviewer.py > "$LOG_DIR/bug2.log" 2>&1 && echo "issue-2: PASS" >> "$LOG_DIR/summary.log" || echo "issue-2: FAIL" >> "$LOG_DIR/summary.log") &
(python reviewer.py > "$LOG_DIR/bug3.log" 2>&1 && echo "issue-3: PASS" >> "$LOG_DIR/summary.log" || echo "issue-3: FAIL" >> "$LOG_DIR/summary.log") &

wait

echo "=== ALL PARALLEL WORKFLOWS COMPLETED ==="
cat "$LOG_DIR/summary.log"