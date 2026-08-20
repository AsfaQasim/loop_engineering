#!/usr/bin/env python3
"""Failure case: Attempt to open a non-existent file."""
import sys

def open_missing_file():
    try:
        with open('missing_data.txt', 'r') as f:
            content = f.read()
            print(f"Read: {content}")
            return True
    except FileNotFoundError as e:
        print(f"FileNotFoundError caught: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Script completes successfully (exit 0) even when error is caught
    open_missing_file()
    sys.exit(0)