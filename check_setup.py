"""Setup check: does the API key in .env work, and can it use our models?

Run it from the launch-in-a-day folder:
    python check_setup.py          # lists models only: uses NO quota
    python check_setup.py --try    # also sends one tiny request to MODEL and BUILDER_MODEL

It never prints the key.

Note: a model being in the list only means your key can SEE it. Whether your free
tier has quota for it is only proven by a real request (--try):
"429 ... limit: 0" means the model is not free for your key.
"""

import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # reads the .env file next to this script

key = os.getenv("GOOGLE_API_KEY", "")
if not key or key.startswith("paste-"):
    raise SystemExit("GOOGLE_API_KEY is missing from .env (or still the placeholder).")

print("Key found in .env. Asking Google which models it can use...")
# One attempt only, so the --try answer is quick and honest (no hidden retries).
client = genai.Client(api_key=key, http_options=types.HttpOptions(
    retry_options=types.HttpRetryOptions(attempts=1)))
names = [m.name.removeprefix("models/") for m in client.models.list()]
print(f"Your key can see {len(names)} models. The Flash-Lite ones (candidates for MODEL):")
for name in sorted(n for n in names if "flash-lite" in n):
    print("   ", name)

print()
for var in ("MODEL", "BUILDER_MODEL"):
    model = os.getenv(var, "")
    if not model:
        print(f"{var} is not set in .env")
        continue
    print(f"{var} = {model!r}: {'visible to your key' if model in names else 'NOT visible to your key'}")
    if "--try" in sys.argv and model in names:
        try:
            client.models.generate_content(model=model, contents="Reply with the single word OK.")
            print("    one tiny request worked: your free tier can use it")
        except Exception as e:
            code = getattr(e, "code", "?")
            if "limit: 0" in str(e):
                print(f"    {code}: quota limit 0, so this model is NOT free for your key")
            elif code == 503:
                print("    503: the model is busy right now (high demand). Try again in a minute.")
            else:
                print(f"    {code}: {str(e)[:120]}")
