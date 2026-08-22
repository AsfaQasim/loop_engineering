# Project 11: Human Gate & API Triggers

An implementation of **A6 (Human Gate Pattern)** from the *Loop Engineering* framework. This project demonstrates controlled workflow execution with human approval gates and API-triggered agent actions.

---

## 📌 Overview

This project implements a two-routine workflow system:
- **Routine A**: A one-off draft execution that generates a review branch/summary for human inspection
- **Routine B**: An API-triggered agent that executes final follow-up actions only after human approval

The system ensures that critical actions require human oversight before execution, preventing unauthorized or premature actions.

---

## 🛠️ How It Works

### Routine A: Draft Execution
1. Generates a draft review branch with summary content
2. Creates a state tracking file (`state_tracker.json`)
3. Outputs draft for human inspection

### Routine B: API-Triggered Agent
1. Protected by single-use Bearer Token authentication
2. Executes final follow-up action only after human approval
3. Maintains execution transcript for audit trail

### Human Gate Pattern
1. Routine A generates draft → Human reviews
2. Human approves → Triggers Routine B via API
3. Routine B executes → Confirms completion

---

## 🚀 Implementation

### Files Created:
- `routine_a.py` - Draft execution script
- `routine_b.py` - API-triggered agent script
- `state_tracker.json` - State tracking file
- `bearer_token.txt` - Single-use authentication token
- `trigger_api.sh` - curl command for API trigger
- `transcript.log` - Execution audit trail

### A6 Checklist Verification:
- ✅ Connectors are pruned
- ✅ Unrestricted git pushes are OFF
- ✅ State tracking file explicitly chosen
- ✅ Human approval required for Routine B

---

## 🔐 Security Features

1. **Single-use Bearer Token**: Each API trigger uses a unique, one-time token
2. **Human Approval Gate**: Routine B cannot execute without prior human approval
3. **State Tracking**: All transitions are logged and auditable
4. **Transcript Logging**: Complete execution history maintained

---

## 📋 Usage

1. Execute Routine A: `python routine_a.py`
2. Review generated draft in `draft_output/`
3. Approve execution by running: `bash trigger_api.sh`
4. Verify completion in `transcript.log`

---

## 📚 Lesson Learned

See `A6_HUMAN_GATE_LESSON.md` for detailed takeaways on implementing human gate patterns in automated workflows.