import subprocess
import sys

#  reviewer

def check_and_review():
    # 1. Run tests / lint checks
    print("[CHECKER] Running verification checks...")
    result = subprocess.run(["python", "-m", "unittest", "test_retriever", "-v"], capture_output=True, text=True)
    
    # 2. Grade Output (Maker-Checker Rule)
    if result.returncode == 0:
        print("RESULT: PASS")
        print("Reason: All tests passed successfully.")
        
        # Open PR automatically on PASS
        print("[CHECKER] Opening Pull Request on GitHub...")
        subprocess.run([
            "gh", "pr", "create",
            "--title", "fix: automated bug fix via reviewer agent",
            "--body", "This PR was automatically created after passing all checker requirements."
        ])
        return True
    else:
        print("RESULT: FAIL")
        print("Reason: Checks failed with the following errors:")
        print(result.stderr or result.stdout)
        return False

if __name__ == "__main__":
    success = check_and_review()
    if not success:
        sys.exit(1)