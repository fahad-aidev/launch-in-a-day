"""Launch Director: takes a startup idea and delegates the work to remote agents over A2A."""

import os
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool

load_dotenv()

OUT_DIR = Path(__file__).resolve().parent.parent / "out"

# --- Teammates. Each is just an address plus a description. --------------------

# A stand-in for an agent that lives somewhere else. The Director never sees the
# Brand agent's code or prompt: only its address and what its card says it does.
brand_agent = RemoteA2aAgent(
    name="brand_agent",
    # Where to find the business card. To use a cloud-hosted Brand agent later,
    # change only this line.
    agent_card="http://localhost:8001/.well-known/agent-card.json",
    # What the Director's model reads to decide WHEN to use this teammate.
    description=(
        "Creates a brand for a startup idea: a company name, a tagline, "
        "a 3-color palette and a simple SVG logo."
    ),
)

builder_agent = RemoteA2aAgent(
    name="builder_agent",
    agent_card="http://localhost:8002/.well-known/agent-card.json",
    description=(
        "Builds a small landing page (index.html + style.css) from brand details: "
        "company name, tagline, 3 hex colors and an SVG logo."
    ),
)

publisher_agent = RemoteA2aAgent(
    name="publisher_agent",
    agent_card="http://localhost:8003/.well-known/agent-card.json",
    description=(
        "Publishes the finished landing page to GitHub and returns the live link. "
        "Irreversible: only use after the user has typed yes."
    ),
)


# --- Code that runs BEFORE every tool call: the human approval gate ---------------
def approval_gate(tool, args, tool_context):
    """The model may WANT to publish, but code only lets it through after a human 'yes'."""
    if tool.name != "publisher_agent":
        return None  # None = every other tool runs normally

    user_said = "".join(p.text or "" for p in tool_context.user_content.parts).strip()
    if not re.fullmatch(r"yes[.!]*", user_said, re.I):
        return {"status": "blocked", "message": "Not published: the user has not typed yes."}

    site_dir = tool_context.state.get("site_dir")
    if not site_dir:
        return {"status": "blocked", "message": "Nothing to publish yet: build a page first."}

    # Attach the exact saved files, so the model never has to copy them.
    html = Path(site_dir, "index.html").read_text(encoding="utf-8")
    css = Path(site_dir, "style.css").read_text(encoding="utf-8")
    args["request"] = (
        "Publish this landing page.\n\n"
        f"```html\n{html.rstrip()}\n```\n\n```css\n{css.rstrip()}\n```"
    )
    return None  # go ahead and call the Publisher


# --- Code that runs after every tool call ----------------------------------------
def save_site_files(tool, args, tool_context, tool_response):
    """When the Builder answers, save its two files to out/ with plain code.

    Big content should not be copied around by the model: code catches the
    Builder's answer, writes the files, and gives the model a short summary.
    """
    if tool.name != "builder_agent":
        return None  # None = leave every other tool's result unchanged

    text = tool_response.get("result", "") if isinstance(tool_response, dict) else str(tool_response)
    html = re.search(r"```html[^\n]*\n(.*?)```", text, re.S | re.I)
    css = re.search(r"```css[^\n]*\n(.*?)```", text, re.S | re.I)
    if not (html and css):
        return {"status": "error", "message": "The builder did not return an html and a css code block."}

    # Only these two file names, only inside out/: the model cannot choose paths.
    launch_dir = OUT_DIR / datetime.now().strftime("launch-%Y%m%d-%H%M%S")
    for folder in (launch_dir, OUT_DIR / "latest"):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(html.group(1), encoding="utf-8")
        (folder / "style.css").write_text(css.group(1), encoding="utf-8")

    tool_context.state["site_dir"] = str(launch_dir)  # remembered for the publish step
    return {"status": "saved", "preview": "out/latest/index.html", "files": ["index.html", "style.css"]}


root_agent = Agent(
    name="launch_director",
    model=os.environ["MODEL"],
    description="Turns a startup idea into a launched landing page by coordinating specialist agents.",
    instruction=(
        "You are the Launch Director of a tiny startup studio.\n"
        "When the user gives you a startup idea, do these steps one at a time:\n"
        "1. Call brand_agent with the idea.\n"
        "2. Wait for its answer. Then call builder_agent with the brand details exactly as "
        "brand_agent returned them, including the full SVG logo.\n"
        "3. Reply to the user in at most 4 lines: the company name, the tagline, "
        "'Preview: out/latest/index.html', and the question "
        "'Type yes to publish this page to GitHub.' Then stop and wait.\n"
        "4. Only if the user replies yes, call publisher_agent (any short request text) "
        "and give the user the links it returns. If the user says anything else, do not publish.\n"
        "If a step returns an error or is blocked, say so in one line."
    ),
    # AgentTool lets the Director call a teammate like a function and get the
    # answer back, so the Director stays in charge of the whole launch.
    tools=[
        AgentTool(agent=brand_agent),
        AgentTool(agent=builder_agent),
        AgentTool(agent=publisher_agent),
    ],
    before_tool_callback=approval_gate,
    after_tool_callback=save_site_files,
)
