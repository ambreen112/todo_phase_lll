#!/bin/bash
cd backend
uvicorn src.main:app --port 8000 --reload &
sleep 2

TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

echo "Testing MCP list_tasks with tag filter..."
curl -X POST "http://localhost:8000/mcp/list_tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -G \
  -d "completed=true" \
  -d "deleted=false" \
  -d "priority=HIGH" \
  -d "tag=red"

echo ""
