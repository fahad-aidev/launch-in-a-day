"""The Brand agent on Google Cloud Run (Step 8).

Same agent as a2a_server.py. Only the address on its Agent Card changes:
Cloud Run serves it over HTTPS at PUBLIC_HOST, so the card must say that,
not localhost. (Other agents read the card to learn where to send messages.)

The Dockerfile starts it with:
    uvicorn brand_agent.cloud_server:a2a_app --host 0.0.0.0 --port $PORT
"""

import os

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .agent import root_agent

# PUBLIC_HOST is set at deploy time, e.g. brand-agent-123456789.us-central1.run.app
a2a_app = to_a2a(
    root_agent, host=os.environ["PUBLIC_HOST"], port=443, protocol="https"
)
