# Project 2: Conditional Loop & Maker-Checker Split (OpenCode)

An implementation of **Concept 5 (Conditional Loop / Run-Until-Done)** and **Concept 11 (Maker-Checker Split)** from the *Loop Engineering* framework.

---

## 📌 Overview

In agentic software engineering, an agent should never be the sole judge of its own work. This project builds a self-healing loop where:
* **Maker (OpenCode Agent):** Inspects test failure logs, modifies source code, and attempts to fix bugs.
* **Checker (Terminal Test Runner):** A deterministic test script (`node math.test.js`) that serves as the ultimate authority on whether code changes pass or fail.

The loop continuously runs until all tests pass or until it hits a maximum iteration cap (6 tries).

---

## 🛠️ Key Concepts Applied

1. **Conditional Loop (Run-Until-Done):** The loop executes iteratively based on task state rather than a fixed timer.
2. **Maker-Checker Split:** Separation between code generation (AI) and outcome validation (command-line test runner).
3. **Safety Ceiling / Cap:** Hard-limiting execution attempts ($MaxTries = 6$) to prevent runaway token spend.

---

## 📁 Repository Structure

```text
project-2/
├── math.js          # Source file containing math functions
├── math.test.js     # Unit test suite verifying functions
├── screenshot.png   # Proof of Beat 2 completion screenshot
└── README.md        # Project documentation