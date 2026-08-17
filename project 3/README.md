# Project 3: Unattended Schedule & The Spine

An implementation of **Concept 6 (Unattended Schedule)** and **Concept 12 (The Spine)** from the *Loop Engineering* framework.

---

## 📌 Overview

This project demonstrates autonomous scheduled execution and persistent state management:
* **Unattended Schedule:** A background process runs without human interaction to scan the codebase for open tasks (`TODO:` comments).
* **The Spine (`progress.md`):** Serves as the central state file and single source of truth. Every run reads existing history before recording new entries to guarantee state continuity and prevent data duplication.

---

## 🛠️ Key Concepts Applied

1. **Unattended Execution:** The loop aggregates project changes automatically without needing prompt-based human intervention.
2. **The Spine Pattern:** `progress.md` acts as system memory. State is loaded, compared, and updated incrementally.
3. **Idempotency:** Re-executing the script on an unchanged codebase results in zero duplicate writes.

---

## 📁 Repository Structure

```text
project-3/
├── progress.md         # The Spine (State Memory File)
├── sync_progress.py    # Unattended scanning & sync script
├── app.py              # Sample source file containing TODO comments
└── README.md           # Project documentation
