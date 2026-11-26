# Container for the Brand agent on Cloud Run (Step 8). Only the Brand agent goes to the cloud.
FROM python:3.13-slim
WORKDIR /app

# Same pinned versions as the laptop.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY brand_agent ./brand_agent

# Cloud Run tells the container which port to listen on through $PORT.
CMD uvicorn brand_agent.cloud_server:a2a_app --host 0.0.0.0 --port $PORT
