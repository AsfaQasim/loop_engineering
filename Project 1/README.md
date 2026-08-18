# Project 1: In-Session Loop Task Monitor (OpenCode)

An implementation of **Concept 4 (In-Session Loop)** from the *Loop Engineering* framework. This project sets up an automated background monitoring loop using OpenCode to check for task completion without requiring active manual terminal polling.

---

## 📌 Overview

In traditional agentic workflows, you continuously prompt the agent to check if a process is done. An **in-session loop** automates this by executing periodic checks until a specific termination condition is met.

This repository demonstrates how to:
1. Run a long-running, detached process in the background.
2. Configure an OpenCode agent loop to periodically inspect state files (`task_complete.done`).
3. Exit cleanly upon completion while alerting the user.

---

## 🛠️ How It Works

1. **Background Process Execution:** A long-running task is spawned as a detached process that writes a sentinel file (`task_complete.done`) upon finishing.
2. **In-Session Loop Evaluation:** OpenCode continuously executes conditional checks using `if exist` (Batch/PowerShell) or `test -f` (Bash) to monitor file state.
3. **Clean Termination:** As soon as `task_complete.done` is detected, OpenCode outputs `FINISHED`, alerts the user, and terminates the loop cleanly.

---

## 🚀 Step-by-Step Instructions

### Step 1: Start the Background Task
Launch a background process that sleeps for a set duration before generating the indicator file:

**On Windows (PowerShell / Command Prompt):**
```cmd
start /B cmd /c "timeout /t 60 >nul && echo DONE > task_complete.done" > task.log 2>&1