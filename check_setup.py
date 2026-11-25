"""Step 0 check: does the API key in .env work, and which Flash-Lite models can it use?

Run it from the launch-in-a-day folder:  python check_setup.py
It never prints the key. Listing models does not use any generation quota.
"""

import os

from dotenv import load_dotenv
from google import genai

load_dotenv()  # reads the .env file next to this script

key = os.getenv("GOOGLE_API_KEY", "")
if not key or key.startswith("paste-"):
    raise SystemExit("GOOGLE_API_KEY is missing from .env (or still the placeholder).")

print("Key found in .env. Asking Google which models it can use...")
client = genai.Client(api_key=key)
names = [m.name.removeprefix("models/") for m in client.models.list()]

print("Flash-Lite models available to this key:")
for name in sorted(n for n in names if "flash-lite" in n):
    print("   ", name)

model = os.getenv("MODEL", "")
status = "available" if model in names else "NOT available, change it in .env"
print(f"MODEL in .env is {model!r}: {status}")
