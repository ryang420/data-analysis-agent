
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "default",
    "stream": true,
    "session_id": "test-session-1",
    "messages": [{"role": "user", "content": "哪些品类销售额最高？"}]
  }'
```