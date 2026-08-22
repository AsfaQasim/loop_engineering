#!/bin/bash
# API Trigger for Routine B
# Single-use Bearer Token authentication

BEARER_TOKEN="qaEWiDWp_82_OKaBCGV9KxkCMV6meHFHcXQtwXnEPTA"
curl -X POST http://localhost:8080/trigger-routine-b \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "execute_followup", "approval": true}'
