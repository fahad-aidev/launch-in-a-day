"""Builder agent: turns brand details into a small landing page (index.html + style.css)."""

import os

from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv()

root_agent = Agent(
    name="builder_agent",
    model=os.environ["MODEL"],
    description=(
        "Builds a small landing page (index.html + style.css) from brand details: "
        "company name, tagline, 3 hex colors and an SVG logo."
    ),
    instruction=(
        "You are a web developer. You receive brand details: a company name, a tagline, "
        "3 hex colors and an SVG logo.\n"
        "Write a small, modern, one-page landing page for this startup.\n"
        "Rules:\n"
        "- index.html links to style.css. Put the SVG logo inline in the HTML, unchanged.\n"
        "- Sections: a hero with logo, name and tagline; 3 short feature points; "
        "a call-to-action button.\n"
        "- Use the 3 brand colors. Mobile friendly.\n"
        "- No JavaScript, no external links, fonts, images or CDNs.\n"
        "- Under 150 lines in total.\n"
        "Reply with exactly two code blocks and nothing else:\n"
        "first ```html with index.html, then ```css with style.css."
    ),
)
