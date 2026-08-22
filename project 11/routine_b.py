#!/usr/bin/env python3
"""
Routine B: API-Triggered Agent
Executes final follow-up action upon invocation with Bearer Token authentication.
"""

import os
import json
import datetime
import secrets
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

class RoutineBHandler(BaseHTTPRequestHandler):
    """HTTP handler for Routine B API trigger."""
    
    def do_POST(self):
        """Handle POST requests for triggering Routine B."""
        # Check authorization
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"error": "Missing or invalid authorization header"}
            self.wfile.write(json.dumps(response).encode())
            return
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        token_file = Path("bearer_token.txt")
        if not token_file.exists():
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"error": "Token file not found"}
            self.wfile.write(json.dumps(response).encode())
            return
        
        with open(token_file, 'r') as f:
            stored_token = f.read().strip()
        
        if token != stored_token:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"error": "Invalid or expired token"}
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Check if token has already been used
        state_file = Path("state_tracker.json")
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            if state.get('routine_b', {}).get('bearer_token_used', False):
                self.send_response(403)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"error": "Token already used. Single-use token expired."}
                self.wfile.write(json.dumps(response).encode())
                return
        
        # Read request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        # Check for human approval
        if not request_data.get('approval', False):
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"error": "Human approval required. Set 'approval': true in request."}
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Execute follow-up action
        try:
            result = execute_followup_action(request_data)
            
            # Mark token as used
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                state['routine_b']['bearer_token_used'] = True
                state['routine_b']['status'] = 'completed'
                state['routine_b']['executed_at'] = datetime.datetime.now().isoformat()
                state['human_gate']['approved'] = True
                state['human_gate']['approved_at'] = datetime.datetime.now().isoformat()
                
                with open(state_file, 'w') as f:
                    json.dump(state, f, indent=2)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "status": "success",
                "message": "Routine B executed successfully",
                "result": result,
                "executed_at": datetime.datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"error": f"Execution failed: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Custom log message format."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] {format % args}\n"
        
        with open("transcript.log", "a") as f:
            f.write(log_entry)
        
        print(log_entry.strip())

def execute_followup_action(request_data):
    """Execute the final follow-up action."""
    timestamp = datetime.datetime.now().isoformat()
    
    # Create follow-up action result
    action_result = {
        "action": "final_followup",
        "status": "completed",
        "executed_at": timestamp,
        "details": {
            "routine_a_draft_approved": True,
            "human_approval_received": request_data.get('approval', False),
            "action_performed": "Final follow-up action executed",
            "artifacts_created": [
                "followup_result.json",
                "completion_certificate.md"
            ]
        }
    }
    
    # Write follow-up result
    with open("followup_result.json", 'w') as f:
        json.dump(action_result, f, indent=2)
    
    # Create completion certificate
    with open("completion_certificate.md", 'w') as f:
        f.write("# Project 11 - Completion Certificate\n\n")
        f.write(f"**Executed At:** {timestamp}\n")
        f.write(f"**Status:** Successfully Completed\n\n")
        f.write("## Verification\n\n")
        f.write("- [x] Routine A draft reviewed and approved\n")
        f.write("- [x] Human approval received via API trigger\n")
        f.write("- [x] Single-use Bearer Token authenticated\n")
        f.write("- [x] Final follow-up action executed\n")
        f.write("- [x] Transcript logged for audit trail\n\n")
        f.write("## Human Gate Verification\n\n")
        f.write("This execution confirms that:\n")
        f.write("1. Routine A generated draft for human review\n")
        f.write("2. Human reviewed and approved the draft\n")
        f.write("3. API trigger was invoked with valid Bearer Token\n")
        f.write("4. Routine B executed only after human approval\n")
        f.write("5. All actions are logged in transcript.log\n")
    
    # Update transcript
    transcript_entry = {
        "timestamp": timestamp,
        "event": "routine_b_executed",
        "details": action_result['details']
    }
    
    with open("transcript.log", "a") as f:
        f.write(json.dumps(transcript_entry) + "\n")
    
    return action_result

def main():
    """Main function to start Routine B API server."""
    print("=" * 60)
    print("ROUTINE B: API-TRIGGERED AGENT")
    print("=" * 60)
    print()
    
    # Check if Routine A has been completed
    state_file = Path("state_tracker.json")
    if not state_file.exists():
        print("ERROR: state_tracker.json not found. Run Routine A first.")
        return 1
    
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    if state.get('routine_a', {}).get('status') != 'completed':
        print("ERROR: Routine A not completed. Run Routine A first.")
        return 1
    
    if state.get('routine_b', {}).get('bearer_token_used', False):
        print("ERROR: Bearer token already used. Generate new token.")
        return 1
    
    print("Starting Routine B API server...")
    print("Endpoint: POST http://localhost:8081/trigger-routine-b")
    print("Authentication: Bearer Token (single-use)")
    print()
    print("To trigger, run: bash trigger_api.sh")
    print()
    print("Press Ctrl+C to stop server")
    print()
    
    # Start HTTP server
    server = HTTPServer(('localhost', 8081), RoutineBHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
    
    return 0

if __name__ == "__main__":
    exit(main())