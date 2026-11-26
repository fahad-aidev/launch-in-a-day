"""Brand agent: turns a startup idea into a name, tagline, palette, vibe and logo."""

import html
import os
import re

from dotenv import load_dotenv
from google.adk.agents import Agent

# Read .env (MODEL, GOOGLE_API_KEY) before we use MODEL below. `adk web` does this
# for us, but uvicorn does not, so the agent loads its own settings either way.
load_dotenv()

HEX = re.compile(r"#[0-9A-Fa-f]{6}")


# A TOOL is a plain Python function. The model never runs it: it asks ADK to run it
# and then reads the result. The docstring and type hints are all the model sees.
def make_logo_svg(name: str, color: str, accent_color: str) -> dict:
    """Draws a polished logo badge: the company's first letter on a gradient tile.

    Args:
        name: The company name, e.g. "Leafy Match".
        color: The dark brand color as a hex code, e.g. "#1B4D3E".
        accent_color: The bright brand color as a hex code, e.g. "#2ECC71".

    Returns:
        A dict with key "svg": the logo as SVG code.
    """
    # The model's input is untrusted: keep one safe letter and only accept hex colors.
    letter = html.escape(name.strip()[:1].upper() or "?")
    dark = color.strip() if HEX.fullmatch(color.strip()) else "#333333"
    bright = accent_color.strip() if HEX.fullmatch(accent_color.strip()) else "#888888"
    gid = f"g{dark[1:]}{bright[1:]}"  # a unique gradient id per palette

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">'
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{bright}"/><stop offset="1" stop-color="{dark}"/>'
        "</linearGradient></defs>"
        f'<rect x="4" y="4" width="112" height="112" rx="32" fill="url(#{gid})"/>'
        '<circle cx="60" cy="60" r="40" fill="none" stroke="#FFFFFF" stroke-opacity=".45" stroke-width="3"/>'
        '<ellipse cx="44" cy="26" rx="30" ry="12" fill="#FFFFFF" fill-opacity=".18"/>'
        '<text x="60" y="63" font-family="system-ui, Arial, sans-serif" font-size="52" font-weight="800" '
        'fill="#FFFFFF" text-anchor="middle" dominant-baseline="middle" '
        f'style="paint-order:stroke" stroke="{dark}" stroke-opacity=".35" stroke-width="4">{letter}</text>'
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
        "a 3-color palette, a design vibe, an emoji and a polished SVG logo."
    ),
    # For ITSELF: how to behave. This is the agent's job description.
    instruction=(
        "You are a brand designer. Given a startup idea:\n"
        "1. Invent a catchy company name, a one-sentence tagline, 3 hex colors "
        "(one dark, one bright, one light), a design vibe and one emoji that fits the idea.\n"
        "2. Call make_logo_svg with the name, the dark color and the bright color.\n"
        "3. Reply with exactly these lines and nothing else:\n"
        "Name: <name>\n"
        "Tagline: <tagline>\n"
        "Colors: <dark> <bright> <light>\n"
        "Vibe: <exactly one of: Playful Pop, Calm Organic, Bold Tech, Luxury Minimal>\n"
        "Emoji: <one emoji>\n"
        "Logo:\n"
        "```svg\n<the svg from the tool, unchanged>\n```"
    ),
    # The functions this agent may ask ADK to run.
    tools=[make_logo_svg],
)
