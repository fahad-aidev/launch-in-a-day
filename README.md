# Launch-in-a-Day

**A team of AI agents that turns a startup idea into a live landing page.**

Someone shouts an idea ("a dating app for houseplants"). A team of agents invents the brand,
designs an animated landing page, shows you a preview, and after you type **yes** publishes it
to GitHub Pages, so everyone can open it on their phone.

Built with **Google ADK** (Agent Development Kit) and the **A2A** (Agent2Agent) protocol,
for a Google workshop.

## Three ideas to take away

1. **An agent** is an LLM + instructions + tools, running in a loop.
2. **ADK** is the toolkit for building agents and teams of agents.
3. **A2A** lets agents that live in different places discover and talk to each other,
   **without seeing each other's insides**: each one only publishes a "business card".

Bonus: **MCP gives an agent hands** (tools), **A2A gives an agent colleagues** (other agents).

## How it works

```
                         ┌─────────────────────────┐
  Your idea  ───────────►│   Launch Director       │  adk web, :8000
                         │   (coordinates the team)│
                         └───┬─────────┬─────────┬─┘
                    A2A      │   A2A   │   A2A   │
              ┌──────────────┘         │         └───────────────┐
              ▼                        ▼                         ▼
     ┌─────────────────┐     ┌─────────────────┐       ┌───────────────────┐
     │  Brand agent    │     │  Builder agent  │       │  Publisher agent  │
     │  :8001          │     │  :8002          │       │  :8003            │
     │  name, tagline, │     │  index.html +   │       │  pushes to GitHub │
     │  colors, vibe,  │     │  style.css      │       │  via the GitHub   │
     │  SVG logo       │     │  (animated)     │       │  MCP server       │
     └─────────────────┘     └─────────────────┘       └─────────┬─────────┘
                                                                 ▼
                                                        GitHub repo + Pages
```

| Agent | Port | Model (from `.env`) | Job |
|---|---|---|---|
| Launch Director | 8000 | `MODEL` | Takes the idea, calls the others, shows a preview, waits for **yes** |
| Brand | 8001 | `MODEL` | Name, tagline, 3 colors, a design vibe, an emoji, a gradient SVG logo (drawn by a Python tool) |
| Builder | 8002 | `BUILDER_MODEL` | A one-page, animated landing page from an art-director design brief |
| Publisher | 8003 | `MODEL` | The **only** agent with the GitHub token. Pushes the page to `sites/<name>-<time>/` |

One launch costs about **10 model calls**.

### Safety built in

- **Human approval:** code checks that your last message is exactly `yes` before the
  Publisher is called. The model cannot talk its way past it.
- **Secrets stay behind a boundary:** the GitHub token lives only in `publisher_agent/.env`
  and is passed only to the GitHub MCP server process. The Publisher folder has no `agent.py`
  or `__init__.py`, so `adk web` can never load it.
- **Guard rails on the MCP tool:** code, not the model, chooses the repo, branch, folder and
  file contents. The model only sees one GitHub tool (`push_files`).
- **Safety filter:** before saving, the Director strips scripts, event handlers and external
  links from the generated page.

## Requirements

- Python **3.11+** (tested with 3.13), [`uv`](https://docs.astral.sh/uv/) and `git`
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
- For publishing only: a **public** demo repo with GitHub Pages turned on (branch `main`,
  folder `/`), a **fine-grained token** limited to that repo with *Contents: Read and write*,
  and the GitHub MCP server installed

## Setup

Run these in the `launch-in-a-day` folder. Mac and Windows differ only in a few commands:

| Step | Mac / Linux | Windows (PowerShell) |
|---|---|---|
| Install uv | `brew install uv` | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Create the environment | `uv venv --python 3.13` | `uv venv --python 3.13` |
| Turn it on (every new terminal) | `source .venv/bin/activate` | `.venv\Scripts\activate` |
| Install packages | `uv pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| Create your settings | `cp .env.example .env` | `copy .env.example .env` |
| Edit your settings | `nano .env` | `notepad .env` |
| GitHub MCP server (publishing) | `brew install github-mcp-server` | `winget install --id GitHub.github-mcp-server -e` |
| Open a generated page | `open out/latest/index.html` | `start out\latest\index.html` |

### Settings (`.env`)

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=<your AI Studio key>
MODEL=gemini-3.5-flash-lite
BUILDER_MODEL=gemini-4-hydrogen
```

For publishing, also copy `publisher_agent/.env.example` to `publisher_agent/.env` and fill in
`GITHUB_TOKEN` and `GITHUB_REPO` (as `owner/name`).

Never commit `.env` files or paste keys anywhere: both `.env` files are in `.gitignore`.

### Check your key and models

```bash
python check_setup.py          # lists models, uses no quota
python check_setup.py --try    # one tiny request to MODEL and BUILDER_MODEL
```

`429 ... limit: 0` means the model is not free for your key. `503` means it is free but busy:
try again in a minute.

## Run it

Open four terminals (activate the environment in each), all in the `launch-in-a-day` folder:

```bash
uvicorn brand_agent.a2a_server:a2a_app --host localhost --port 8001
uvicorn builder_agent.a2a_server:a2a_app --host localhost --port 8002
uvicorn publisher_agent.a2a_server:a2a_app --host localhost --port 8003
adk web --port 8000
```

Then:

1. Optional: `python preflight.py` checks settings, all four servers and GitHub Pages
   (no model calls).
2. Open http://127.0.0.1:8000, pick **launch_director**, start a new session and type an idea.
3. Open the preview: `out/latest/index.html`.
4. Type **yes** to publish. You get a live link (`https://<owner>.github.io/<repo>/sites/...`).
   GitHub Pages needs about a minute before the link works.

Each agent's business card is at `http://localhost:<port>/.well-known/agent-card.json`.

## X-ray: what A2A looks like on the wire

A2A is plain JSON over HTTP. With the Brand agent running:

```bash
curl -s http://localhost:8001/ -H "Content-Type: application/json" -H "A2A-Version: 1.0" -d @xray/send_message.json | python3 -m json.tool
```

You get back a **task** with an ID, a state (`TASK_STATE_COMPLETED`) and the result as an
artifact. See [xray/README.md](xray/README.md). For a visual view, use the
[A2A Inspector](https://github.com/a2aproject/a2a-inspector): `a2a-inspector -a localhost:8001`.

## Project layout

```
launch-in-a-day/
├── .env.example              # settings template (copy to .env)
├── requirements.txt          # pinned versions
├── check_setup.py            # is my key working? which models can it use?
├── preflight.py              # demo-day checks, no model calls
├── brand_agent/
│   ├── agent.py              # the agent + its make_logo_svg tool
│   └── a2a_server.py         # exposes it over A2A on :8001
├── builder_agent/
│   ├── agent.py              # the agent + its design brief
│   └── a2a_server.py         # :8002
├── publisher_agent/
│   ├── publisher.py          # the agent + GitHub MCP tool + guard rails
│   ├── a2a_server.py         # :8003
│   └── .env.example          # Publisher-only secrets template
├── launch_director/
│   └── agent.py              # coordinator: remote agents, approval gate, safety filter
├── xray/                     # a raw A2A request for curl
└── out/                      # generated pages (git-ignored)
```

## Troubleshooting

| You see | It means |
|---|---|
| `KeyError: 'MODEL'` or `'BUILDER_MODEL'` | That line is missing from `.env` |
| `429 ... limit: 0` | The model is not on your free tier: pick another in `.env` |
| `503 ... high demand` | The free model is busy. The Builder retries the same model a few times; otherwise try again shortly |
| A launch is slow | The Builder's model can take from 20 seconds to a few minutes on the free tier |
| `VERSION_NOT_SUPPORTED` from curl | Add the header `A2A-Version: 1.0` |
| `404` on `/.well-known/agent.json` | The path is `agent-card.json` in A2A 1.0 |
| Publishing fails with 403 | The token needs *Contents: Read and write* on the demo repo |
| The live link shows 404 | Wait about a minute for GitHub Pages |

## Versions and gotchas

Pinned: `google-adk[a2a,mcp]==2.15.1`, `a2a-sdk==1.3.1`, `mcp==2.3.0`. Things that changed
recently and break older tutorials:

- Docs are at [adk.dev](https://adk.dev). The Agent Card path is `/.well-known/agent-card.json`.
- MCP support in ADK 2.x needs the `mcp` extra: `google-adk[a2a,mcp]`.
- `mcp` 2.x renamed `FastMCP` to `MCPServer`.
- Tutorials that import `A2AStarletteApplication` are pre-1.0 and will not work.
- `adk web` lists, and may load, every folder that has `agent.py` or `__init__.py`.

Free-tier prompts may be used to improve Google products: don't enter personal data.
