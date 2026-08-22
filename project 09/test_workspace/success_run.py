#!/usr/bin/env python3
"""Success case: Summarize recent commits into a file."""
import subprocess
import sys

def summarize_commits():
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', '-5'],
            capture_output=True,
            text=True,
            cwd=r'F:\loop_Engineering'
        )
        
        if result.returncode != 0:
            print(f"Git command failed: {result.stderr}")
            return False
            
        commits = result.stdout.strip().split('\n')
        
        with open('commit_summary.txt', 'w') as f:
            f.write("Recent Commits Summary:\n")
            f.write("=" * 30 + "\n")
            for commit in commits:
                f.write(f"• {commit}\n")
        
        print(f"Success! Created commit_summary.txt with {len(commits)} commits.")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if summarize_commits() else 1)