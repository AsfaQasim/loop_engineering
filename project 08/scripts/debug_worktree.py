#!/usr/bin/env python3
"""Debug script to test worktree environment."""
import subprocess
import sys
from pathlib import Path
from worktree_manager import create_worktree, cleanup_worktree

PROJECT = Path(__file__).parent.parent
print(f"Creating worktree from {PROJECT}...")
wt = create_worktree(PROJECT)
print(f"Worktree at: {wt.path}")

# Check what's in the worktree
import os
print(f"\nWorktree contents:")
for f in os.listdir(wt.path):
    print(f"  {f}")

# Try running tests
print(f"\nRunning tests in worktree...")
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
    capture_output=True, text=True, cwd=wt.path,
)
print(f"Return code: {result.returncode}")
print(f"STDOUT:\n{result.stdout}")
print(f"STDERR:\n{result.stderr}")

cleanup_worktree(wt)
print("\nWorktree cleaned up.")
