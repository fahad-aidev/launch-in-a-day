"""Brand agent: turns a startup idea into a name, a tagline, a color palette and a logo."""

import html
import os
import re

from dotenv import load_dotenv
from google.adk.agents import Agent

# Read .env (MODEL, GOOGLE_API_KEY) before we use MODEL below. `adk web` does this
# for us, but uvicorn does not, so the agent loads its own settings either way.
load_dotenv()


# A TOOL is a plain Python function. The model never runs it: it asks ADK to run it
# and then reads the result. The docstring and type hints are all the model sees.
def make_logo_svg(name: str, color: str) -> dict:
    """Draws a simple round logo with the first letter of the company name.

    Args:
        name: The company name, e.g. "Leafy Match".
        color: Background color of the logo as a hex code, e.g. "#2E7D32".

    Returns:
        A dict with key "svg": the logo as SVG code.
    """
    # The model's input is untrusted: keep one safe letter and only accept a hex color.
    letter = html.escape(name.strip()[:1].upper() or "?")
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", color.strip()):
        color = "#333333"

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">'
        f'<circle cx="60" cy="60" r="56" fill="{color.strip()}"/>'
        '<text x="60" y="62" font-family="Arial, sans-serif" font-size="64" font-weight="bold" '
        f'fill="#FFFFFF" text-anchor="middle" dominant-baseline="middle">{letter}</text>'
        "</svg>"
    )
    return {"svg": svg}


root_agent = Agent(
    # A short, unique ID. No spaces.
    name="brand_agent",
    # Which LLM to use. Read from .env so we can swap models without touching code.
    model=os.environ["MODEL"],  # fails with a clear KeyError: 'MODEL' if .env is missing it
    # For OTHER agents: what this agent is good for (used later for delegation).
    description=(
        "Creates a brand for a startup idea: a company name, a tagline, "
        "a 3-color palette and a simple SVG logo."
    ),
    # For ITSELF: how to behave. This is the agent's job description.
    instruction=(
        "You are a brand designer. Given a startup idea:\n"
        "1. Invent a catchy company name, a one-sentence tagline and 3 hex colors.\n"
        "2. Call make_logo_svg with the name and the darkest of your 3 colors.\n"
        "3. Reply with exactly these lines and nothing else:\n"
        "Name: <name>\n"
        "Tagline: <tagline>\n"
        "Colors: <3 hex colors>\n"
        "Logo:\n"
        "```svg\n<the svg from the tool, unchanged>\n```"
    ),
    # The functions this agent may ask ADK to run.
    tools=[make_logo_svg],
)
