#!/usr/bin/env python3
"""
Trigger Routine B via API
"""

import requests
import json
from pathlib import Path

def trigger_routine_b():
    """Trigger Routine B using the Bearer Token."""
    
    # Read bearer token
    token_file = Path("bearer_token.txt")
    if not token_file.exists():
        print("ERROR: bearer_token.txt not found")
        return False
    
    with open(token_file, 'r') as f:
        token = f.read().strip()
    
    # API endpoint
    url = "http://localhost:8081/trigger-routine-b"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Request body
    data = {
        "action": "execute_followup",
        "approval": True
    }
    
    print(f"Triggering Routine B...")
    print(f"URL: {url}")
    print(f"Token: {token[:10]}...")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\nRoutine B executed successfully!")
            return True
        else:
            print(f"\nRoutine B execution failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to Routine B server")
        print("Make sure routine_b.py is running")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    trigger_routine_b()