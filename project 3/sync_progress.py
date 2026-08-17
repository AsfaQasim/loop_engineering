import os
import re
from datetime import datetime

SPINE_FILE = "progress.md"

def get_recorded_todos(spine_path):
    """Reads the Spine file to extract already recorded TODO identifiers."""
    if not os.path.exists(spine_path):
        return set()
    
    with open(spine_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract existing TODO text from markdown list items
    recorded = set(re.findall(r"-\s*\[.*?\]\s*(.*)", content))
    return recorded

def scan_repo_for_todos():
    """Scans repository files for open TODO comments."""
    found_todos = []
    ignored_dirs = {".git", "__pycache__", "node_modules", ".venv"}

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            if file.endswith((".py", ".js", ".ts", ".md", ".json")) and file != SPINE_FILE:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if "TODO:" in line:
                                # Skip lines in sync_progress.py that contain TODO: as part of code logic
                                if os.path.basename(file_path) == "sync_progress.py":
                                    continue
                                todo_text = line.split("TODO:", 1)[1].strip()
                                # Clean relative path formatting
                                clean_path = os.path.relpath(file_path, ".").replace("\\", "/")
                                found_todos.append(f"`{clean_path}:{line_num}` — {todo_text}")
                except Exception:
                    continue
    return found_todos

def run_unattended_loop():
    """Main loop execution: reads Spine, gathers diff, and appends state."""
    # Step 1: Read current state from The Spine
    recorded_todos = get_recorded_todos(SPINE_FILE)
    
    # Step 2: Gather current repository state
    current_todos = scan_repo_for_todos()
    
    # Step 3: Compute state diff (unrecorded TODOs only)
    new_todos = [todo for todo in current_todos if todo not in recorded_todos]
    
    # Step 4: Conditional update
    if not new_todos:
        print("[UNATTENDED LOOP] Spine is up-to-date. No new TODOs recorded.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_block = f"\n### Run on {timestamp}\n"
    for todo in new_todos:
        entry_block += f"- [ ] {todo}\n"

    # Step 5: Append to Spine
    with open(SPINE_FILE, "a", encoding="utf-8") as f:
        f.write(entry_block)

    print(f"[UNATTENDED LOOP] State updated. Appended {len(new_todos)} new entry/entries to {SPINE_FILE}.")

if __name__ == "__main__":
    run_unattended_loop()