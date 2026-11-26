# Workshop commands

Run these from the `launch-in-a-day` folder.

1. Install uv (official page: https://docs.astral.sh/uv/getting-started/installation/)

   macOS / Linux:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   or with Homebrew:
   ```bash
   brew install uv
   ```
   Windows (PowerShell):
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
   or with WinGet:
   ```powershell
   winget install --id=astral-sh.uv  -e
   ```

2. Creating virtual environment using:
   ```bash
   uv venv --python 3.13
   ```

3. Initializing the env:
   ```bash
   source .venv/bin/activate
   ```

4. Install requirements:
   ```bash
   uv pip install -r requirements.txt
   ```

5. Checking if adk has been installed:
   ```bash
   adk --help
   ```

6. Copying the command:
   ```bash
   cp .env.example .env
   ```

7. Run and check the key file:
   ```bash
   python check_setup.py
   ```

8. Run ADK:
   ```bash
   adk web --port 8000
   ```

9. For all agents:
   ```bash
   uvicorn brand_agent.a2a_server:a2a_app --host localhost --port 8001
   ```
   ```bash
   uvicorn builder_agent.a2a_server:a2a_app --host localhost --port 8002
   ```
   ```bash
   uvicorn publisher_agent.a2a_server:a2a_app --host localhost --port 8003
   ```

10. macOS:
    ```bash
    brew install github-mcp-server
    ```
    for windows:
    ```powershell
    winget install --id GitHub.github-mcp-server -e
    ```

11. Generate Github PAT for launch product repo: https://github.com/settings/personal-access-tokens/new

    Put it only in `publisher_agent/.env` as `GITHUB_TOKEN=...`. Never paste the token into this file or commit it.

12. Use to install gcloud cli:
    ```bash
    brew install --cask gcloud-cli
    ```

13. For gcloud. https://docs.cloud.google.com/sdk/docs/install-sdk#windows

14. auth login:
    ```bash
    gcloud auth login
    ```

15. Run command for project in terminal:
    ```bash
    PROJECT_ID=your-project-id; REGION=us-central1; gcloud config set project $PROJECT_ID; PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)'); SA=$PROJECT_NUMBER-compute@developer.gserviceaccount.com; echo $PROJECT_NUMBER
    ```

16. Enable APIs:
    ```bash
    gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com
    ```
    ```bash
    gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$SA --role=roles/cloudbuild.builds.builder
    ```
    ```bash
    gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$SA --role=roles/aiplatform.user
    ```

17. check what to upload:
    ```bash
    gcloud meta list-files-for-upload
    ```

18. Deploy brand agent on gcloud:
    ```bash
    gcloud run deploy brand-agent --source . --region $REGION --allow-unauthenticated --max-instances 1 --set-env-vars GOOGLE_GENAI_USE_ENTERPRISE=TRUE,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=global,MODEL=gemini-3.5-flash-lite,PUBLIC_HOST=brand-agent-$PROJECT_NUMBER.$REGION.run.app
    ```

19. ```bash
    curl https://brand-agent-$PROJECT_NUMBER.$REGION.run.app/.well-known/agent-card.json
    ```
