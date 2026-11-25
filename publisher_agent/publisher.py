"""Publisher agent: the ONLY agent that holds the GitHub token.

It receives a finished landing page over A2A and pushes it to GitHub using the
GitHub MCP server (MCP gives the agent "hands"). Code guards decide what is
pushed and where; the model only decides to push and writes the commit message.

This folder has no agent.py and no __init__.py ON PURPOSE: `adk web` lists (and
may load) every folder that has either one. Without them, the dev UI can never
load the Publisher or its GitHub token. The only way in is A2A on port 8003.
"""

import os
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

HERE = Path(__file__).resolve().parent
load_dotenv(HERE.parent / ".env")  # shared settings: GOOGLE_API_KEY, MODEL
load_dotenv(HERE / ".env")  # Publisher-only secrets: GITHUB_TOKEN, GITHUB_REPO

OWNER, REPO = os.environ["GITHUB_REPO"].split("/")
BRANCH = "main"  # GitHub Pages serves this branch

# --- MCP: the GitHub MCP server runs as a small local program next to this agent.
github_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=os.getenv("GITHUB_MCP_COMMAND", "github-mcp-server"),
            args=["stdio"],
            # The token goes ONLY to this child process (not even our API key does).
            env={
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ["GITHUB_TOKEN"],
                "GITHUB_TOOLSETS": "repos",
                "PATH": os.environ.get("PATH", ""),
                "HOME": os.environ.get("HOME", ""),
            },
        ),
        timeout=30,
    ),
    tool_filter=["push_files"],  # the model sees exactly one GitHub tool
)


def _site_files(text: str) -> dict | None:
    """Finds the ```html and ```css blocks in the message from the Director."""
    html = re.search(r"```html[^\n]*\n(.*?)```", text, re.S | re.I)
    css = re.search(r"```css[^\n]*\n(.*?)```", text, re.S | re.I)
    if not (html and css):
        return None
    return {"index.html": html.group(1), "style.css": css.group(1)}


def _slug(html: str) -> str:
    title = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    words = re.sub(r"[^a-z0-9]+", "-", (title.group(1) if title else "site").lower())
    return words.strip("-")[:30].strip("-") or "site"


# --- Guard rails around the MCP tool ---------------------------------------------
def guard_push(tool, args, tool_context):
    """Runs BEFORE every GitHub call. Code, not the model, decides what and where."""
    if tool.name != "push_files":
        return {"error": "Only push_files is allowed."}

    request = "".join(p.text or "" for p in tool_context.user_content.parts)
    files = _site_files(request)
    if files is None:
        return {"error": "The request did not contain index.html and style.css."}

    # A new folder per launch: nothing is ever overwritten, nothing is force-pushed.
    folder = f"sites/{_slug(files['index.html'])}-{datetime.now():%Y%m%d-%H%M%S}"
    message = (args.get("message") or "Launch a new site").strip()[:72]
    args.clear()
    args.update(
        owner=OWNER,
        repo=REPO,
        branch=BRANCH,
        message=message,
        files=[{"path": f"{folder}/{name}", "content": body} for name, body in files.items()],
    )
    return None  # None = go ahead with the (now safe) call


def report_links(tool, args, tool_context, tool_response):
    """Runs AFTER the GitHub call: turn GitHub's reply into the links people need."""
    if tool.name != "push_files":
        return None
    if tool_response.get("isError") or tool_response.get("is_error"):
        details = " ".join(c.get("text", "") for c in tool_response.get("content", []))
        return {"status": "error", "message": details[:300]}
    folder = args["files"][0]["path"].rsplit("/", 1)[0]
    return {
        "status": "published",
        "pages_url": f"https://{OWNER.lower()}.github.io/{REPO}/{folder}/",
        "code_url": f"https://github.com/{OWNER}/{REPO}/tree/{BRANCH}/{folder}",
    }


root_agent = Agent(
    name="publisher_agent",
    model=os.environ["MODEL"],
    description=(
        "Publishes a finished landing page (index.html + style.css) to the team's GitHub "
        "repo and returns the live link."
    ),
    instruction=(
        "You publish landing pages to GitHub.\n"
        "Call push_files exactly once. Write a short commit message like "
        "'Launch <company name>'. For owner, repo, branch and files pass empty values: "
        "they are filled in automatically.\n"
        "Then reply with two lines: 'Live page: <pages_url>' and 'Code: <code_url>' from "
        "the tool result. If the tool returns an error, reply with it in one line."
    ),
    tools=[github_tools],
    before_tool_callback=guard_push,
    after_tool_callback=report_links,
)
