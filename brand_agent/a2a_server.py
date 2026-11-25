"""Expose the Brand agent over A2A on port 8001.

The agent itself (agent.py) is unchanged. This file only gives it an address
and a public "business card" (the Agent Card).

Run from the launch-in-a-day folder:
    uvicorn brand_agent.a2a_server:a2a_app --host localhost --port 8001
Then open:
    http://localhost:8001/.well-known/agent-card.json
"""

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .agent import root_agent

# Wrap the agent in a small web app. The port here is only written into the
# Agent Card; it must match the --port you give uvicorn.
a2a_app = to_a2a(root_agent, port=8001)
