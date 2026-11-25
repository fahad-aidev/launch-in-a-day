"""Expose the Publisher agent over A2A on port 8003.

Run from the launch-in-a-day folder:
    uvicorn publisher_agent.a2a_server:a2a_app --host localhost --port 8003
Agent Card:
    http://localhost:8003/.well-known/agent-card.json
"""

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .publisher import root_agent

a2a_app = to_a2a(root_agent, port=8003)
