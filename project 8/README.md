# Project 8: Capstone - Unattended Autonomous Loop

> **Loop Engineering · Module 08**  
> Production integration of Heartbeat, Worktree, Skill, Maker-Checker, Connector, Spine, and Budget Guards for automated recurring chores.

---

## 📌 Project Overview

Project 8 is the capstone synthesis of the entire Autonomous Agent Architecture curriculum. It automates a recurring, real-world development chore—specifically a **Lint Sweep & Dependency Security Audit**—running fully unattended with end-to-end safety guarantees, budget circuits, and zero-replay observability.

---

## ⚙️ System Architecture (All 6 Parts Integration)

| Component | Architecture Role | Implementation Detail |
| :--- | :--- | :--- |
| **The Heartbeat** | Trigger Mechanism | Scheduled execution via OpenCode runner / cron beat. |
| **Worktree** | Context Isolation | Creates and cleans up `worktree-capstone-audit` workspace. |
| **Skill** | Domain Logic | Executes `scripts/audit_chore.py` for Python formatting & dep scanning. |
| **Maker-Checker** | Verification Loop | Maker fixes formatting; Checker runs 46 test cases to ensure zero breakages. |
| **Connector** | External Delivery | Submits Pull Requests to GitHub repository upon test passage. |
| **The Spine** | Telemetry & Audit Log | Writes persistent beat diagnostic entries directly into `progress.md`. |
| **Budget Guards** | Financial Safety | Hard limits on retries (max 2) and token spending thresholds. |

---

## 🚀 Quick Start & Execution

Execute the Capstone loop inside the target repository:

```bash
cd learn_humanoid_robot

opencode run "Set up Project 8 Capstone Loop for recurring chore 'Lint Sweep & Dependency Audit':

1. Create a script or workflow that spins up isolated git worktree 'worktree-capstone-audit'.
2. Implement a specialized skill in scripts/audit_chore.py to check formatting and outdated dependencies.
3. Apply Maker-Checker loop: Maker fixes formatting; Checker runs test suite.
4. Log execution timestamps, token usage estimate, and verdict into progress.md.
5. Enforce budget guard: limit max retries to 2 and log 'NEEDS HUMAN INTERVENTION' upon failure."