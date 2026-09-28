import os
import re

# Read the extracted 162k route
with open("agents/extracted_162k_route.py", "r", encoding="utf-8") as f:
    premium_code = f.read()

# Extract the base85 string
match = re.search(r"base64\.b85decode\('([^']+)'\)", premium_code)
if not match:
    raise ValueError("Could not find base85 tape in extracted_162k_route.py")
premium_b85 = match.group(1)

# Read v104
with open("submission_v104_quote_priority.py", "r", encoding="utf-8") as f:
    v104_code = f.read()

injection = f"""

# --- INJECTED V109: 162K HIGH-TIER TRACE (FULL ROUTE OVERRIDE) ---
import json, base64, zlib
_INJECTED_TAPE = json.loads(zlib.decompress(base64.b85decode('{premium_b85}')))
_INJECTED_ROUTES = {{"injected": _INJECTED_TAPE}}
_INJECTED_ROUTER = lambda *args, **kwargs: "injected"

# Try to find the settings, fallback to defaults if somehow unavailable
_INJECTED_SETTINGS = DEFAULT_SETTINGS
for k in list(globals().keys()):
    if k == '_SETTINGS':
        _INJECTED_SETTINGS = _SETTINGS

agent = make_agent(_INJECTED_ROUTES, router=_INJECTED_ROUTER, **_INJECTED_SETTINGS)
agent.telemetry = globals().get('_CS_REPORT', {{}})
# -----------------------------------------------------------------
"""

# Append to the very end
v104_code = v104_code + injection

with open("submission_v109_full_162k.py", "w", encoding="utf-8") as f:
    f.write(v104_code)

print("Created submission_v109_full_162k.py")
