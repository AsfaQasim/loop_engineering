import os
import sys
import time
from datetime import datetime

TARGET_FILE = "missing_file.py"
MAX_RETRIES = 3
RETRY_DELAY = 0.5  # seconds between retries.


def check_file_exists(filepath, retries=MAX_RETRIES):
    for attempt in range(1, retries + 1):
        if os.path.exists(filepath):
            return True, attempt
        if attempt < retries:
            time.sleep(RETRY_DELAY)
    return False, retries


def log_failure(filepath, error_reason):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"\n## [{timestamp}] - EXECUTION FAILED\n"
        f"- Status: NEEDS HUMAN INTERVENTION\n"
        f"- Target: {filepath}\n"
        f"- Error: {error_reason}\n"
    )
    with open("progress.md", "a") as f:
        f.write(log_entry)
    print(f"ERROR: {error_reason}. Logged to progress.md.")
    sys.exit(1)


if __name__ == "__main__":
    found, attempts = check_file_exists(TARGET_FILE)
    if not found:
        log_failure(
            TARGET_FILE,
            f"File '{TARGET_FILE}' not found after {attempts} retry attempts"
        )
    else:
        print(f"File '{TARGET_FILE}' found on attempt {attempts}.")
        sys.exit(0)