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

# Read 014_robust_trace.py
with open("agents/014_robust_trace.py", "r", encoding="utf-8") as f:
    robust_code = f.read()

# Replace the tape in 014_robust_trace.py
robust_code = re.sub(
    r"base64\.b85decode\('([^']+)'\)",
    f"base64.b85decode('{premium_b85}')",
    robust_code,
    count=1
)

# Also update the docstring to indicate this is V107
robust_code = robust_code.replace("Agent V032", "Agent V107 (162k High-Tier Trace + Front-Runner Market)")

with open("submission_v107_extracted_162k.py", "w", encoding="utf-8") as f:
    f.write(robust_code)

print("Created submission_v107_extracted_162k.py")
