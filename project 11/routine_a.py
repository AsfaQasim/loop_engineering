#!/usr/bin/env python3
"""
Routine A: Draft Execution
Generates a draft review branch/summary for human inspection.
"""

import os
import json
import datetime
from pathlib import Path

def create_draft_output():
    """Create draft output directory and files."""
    draft_dir = Path("draft_output")
    draft_dir.mkdir(exist_ok=True)
    
    # Generate draft content
    timestamp = datetime.datetime.now().isoformat()
    draft_content = {
        "draft_id": f"draft_{int(datetime.datetime.now().timestamp())}",
        "created_at": timestamp,
        "status": "pending_review",
        "summary": {
            "title": "Project 11 Draft Review",
            "description": "This draft requires human approval before final execution.",
            "items": [
                "Routine A execution completed successfully",
                "Draft review branch generated",
                "State tracking file initialized",
                "Awaiting human approval for Routine B"
            ]
        },
        "metadata": {
            "version": "1.0",
            "author": "OpenCode Agent",
            "project": "Project 11 - Human Gate & API Triggers"
        }
    }
    
    # Write draft file
    draft_file = draft_dir / "draft_review.json"
    with open(draft_file, 'w') as f:
        json.dump(draft_content, f, indent=2)
    
    # Create summary markdown
    summary_md = draft_dir / "DRAFT_SUMMARY.md"
    with open(summary_md, 'w') as f:
        f.write(f"# Draft Review Summary\n\n")
        f.write(f"**Draft ID:** {draft_content['draft_id']}\n")
        f.write(f"**Created:** {timestamp}\n")
        f.write(f"**Status:** {draft_content['status']}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"{draft_content['summary']['description']}\n\n")
        f.write(f"## Items\n\n")
        for item in draft_content['summary']['items']:
            f.write(f"- {item}\n")
        f.write(f"\n## Next Steps\n\n")
        f.write(f"1. Review this draft carefully\n")
        f.write(f"2. If approved, execute Routine B using the API trigger\n")
        f.write(f"3. Verify completion in transcript.log\n")
    
    return draft_content, draft_file

def update_state_tracker(draft_data):
    """Update state tracking file."""
    state_file = Path("state_tracker.json")
    
    state = {
        "project": "Project 11",
        "phase": "routine_a_complete",
        "routine_a": {
            "status": "completed",
            "draft_id": draft_data['draft_id'],
            "executed_at": datetime.datetime.now().isoformat(),
            "output_files": [
                "draft_output/draft_review.json",
                "draft_output/DRAFT_SUMMARY.md"
            ]
        },
        "routine_b": {
            "status": "pending_human_approval",
            "requires_approval": True,
            "approval_timestamp": None,
            "bearer_token_used": False
        },
        "human_gate": {
            "approval_required": True,
            "approved": False,
            "approved_at": None
        }
    }
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    return state

def main():
    """Main execution function."""
    print("=" * 60)
    print("ROUTINE A: DRAFT EXECUTION")
    print("=" * 60)
    print()
    
    # Create draft output
    print("[1/3] Creating draft output...")
    draft_data, draft_file = create_draft_output()
    print(f"  [OK] Draft created: {draft_file}")
    
    # Update state tracker
    print("[2/3] Updating state tracker...")
    state = update_state_tracker(draft_data)
    print(f"  [OK] State tracker updated: state_tracker.json")
    
    # Generate API trigger command
    print("[3/3] Generating API trigger command...")
    token_file = Path("bearer_token.txt")
    if not token_file.exists():
        import secrets
        token = secrets.token_urlsafe(32)
        with open(token_file, 'w') as f:
            f.write(token)
    else:
        with open(token_file, 'r') as f:
            token = f.read().strip()
    
    # Create trigger script
    trigger_script = Path("trigger_api.sh")
    with open(trigger_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# API Trigger for Routine B\n")
        f.write("# Single-use Bearer Token authentication\n\n")
        f.write(f'BEARER_TOKEN="{token}"\n')
        f.write("curl -X POST http://localhost:8080/trigger-routine-b \\\n")
        f.write("  -H \"Authorization: Bearer $BEARER_TOKEN\" \\\n")
        f.write("  -H \"Content-Type: application/json\" \\\n")
        f.write("  -d '{\"action\": \"execute_followup\", \"approval\": true}'\n")
    
    print(f"  [OK] Trigger script created: trigger_api.sh")
    print(f"  [OK] Bearer token saved: bearer_token.txt")
    
    print()
    print("=" * 60)
    print("ROUTINE A COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review draft in draft_output/ directory")
    print("2. If approved, run: bash trigger_api.sh")
    print("3. Check transcript.log for execution details")
    print()
    
    return 0

if __name__ == "__main__":
    exit(main())