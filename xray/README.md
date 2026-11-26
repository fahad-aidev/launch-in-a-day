# X-ray: what A2A looks like on the wire

A2A is plain JSON over HTTP. `send_message.json` is a complete A2A 1.0 request:
"here is a message from a user, please handle it" (JSON-RPC method `SendMessage`).

With the Brand agent running on port 8001, send it from the project folder:

```bash
curl -s http://localhost:8001/ -H "Content-Type: application/json" -H "A2A-Version: 1.0" -d @xray/send_message.json | python3 -m json.tool
```

What comes back is a **task**:

- `id` and `contextId`: the task's ID and the conversation it belongs to.
- `status.state`: `TASK_STATE_COMPLETED` (other states include working, input required, failed).
- `artifacts`: the result, here the brand text.
- `history`: the user's message (`ROLE_USER`) and the agent's answer (`ROLE_AGENT`).

Without the `A2A-Version: 1.0` header, the server assumes the older 0.3 protocol and
answers with the error `VERSION_NOT_SUPPORTED`.

Cost: one request to the Brand agent is about 2 model calls.
