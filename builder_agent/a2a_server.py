"""Expose the Builder agent over A2A on port 8002.

Run from the launch-in-a-day folder:
    uvicorn builder_agent.a2a_server:a2a_app --host localhost --port 8002
Agent Card:
    http://localhost:8002/.well-known/agent-card.json
"""

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .agent import root_agent

a2a_app = to_a2a(root_agent, port=8002)
