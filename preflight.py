"""Demo-day pre-flight check. Run it once before the audience arrives.

    python preflight.py

It makes NO model calls and never prints secrets. It checks settings, the four
servers, the GitHub MCP server program, and that GitHub Pages is reachable.
"""

import shutil
from pathlib import Path

import httpx
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent
AGENTS = {"brand_agent": 8001, "builder_agent": 8002, "publisher_agent": 8003}
problems = 0


def check(ok: bool, label: str, fix: str = "") -> None:
    global problems
    print(("  OK   " if ok else "  FAIL ") + label + ("" if ok else f"\n         -> {fix}"))
    problems += not ok


print("Settings")
env = dotenv_values(ROOT / ".env")
check(bool(env.get("GOOGLE_API_KEY")) and "paste-" not in env.get("GOOGLE_API_KEY", ""),
      "GOOGLE_API_KEY is set in .env", "add your AI Studio key to .env")
check(bool(env.get("MODEL")), f"MODEL = {env.get('MODEL')}", "add MODEL=... to .env")
check(bool(env.get("BUILDER_MODEL")), f"BUILDER_MODEL = {env.get('BUILDER_MODEL')}",
      "add BUILDER_MODEL=... to .env")
pub = dotenv_values(ROOT / "publisher_agent" / ".env")
token_ok = bool(pub.get("GITHUB_TOKEN")) and "paste-" not in pub.get("GITHUB_TOKEN", "")
check(token_ok, "GITHUB_TOKEN is set in publisher_agent/.env", "add the fine-grained token")
repo = pub.get("GITHUB_REPO", "")
check("/" in repo and "your-" not in repo, f"GITHUB_REPO = {repo}", "set GITHUB_REPO=owner/name")
check(shutil.which("github-mcp-server") is not None, "github-mcp-server is installed",
      "brew install github-mcp-server")

print("\nServers")
for name, port in AGENTS.items():
    try:
        card = httpx.get(f"http://localhost:{port}/.well-known/agent-card.json", timeout=3).json()
        check(card.get("name") == name, f"{name} answers on :{port}", f"wrong agent on port {port}")
    except httpx.HTTPError:
        check(False, f"{name} answers on :{port}",
              f"start it: uvicorn {name}.a2a_server:a2a_app --host localhost --port {port}")
try:
    apps = httpx.get("http://127.0.0.1:8000/list-apps", timeout=3).json()
    check("launch_director" in apps, "adk web is up on :8000 with launch_director", "restart adk web")
except httpx.HTTPError:
    check(False, "adk web is up on :8000", "start it: adk web --port 8000")

print("\nInternet")
if "/" in repo:
    owner, name = repo.split("/", 1)
    url = f"https://{owner.lower()}.github.io/{name}/"
    try:
        status = httpx.get(url, timeout=8, follow_redirects=True).status_code
        check(status < 500, f"GitHub Pages reachable ({url} -> HTTP {status})", "check Wi-Fi")
    except httpx.HTTPError:
        check(False, f"GitHub Pages reachable ({url})", "no internet: use the out/latest fallback")

print("\nAll good. Break a leg!" if problems == 0 else f"\n{problems} problem(s) to fix first.")
