import json
import zlib
import base64
import re

actions = json.load(open('ai_after_hours_no_dig.json'))
compressed = base64.b85encode(zlib.compress(json.dumps(actions).encode('utf-8'))).decode('ascii')

with open('agents/v057_generalized_spoiler.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Find the _ACTIONS assignment line
new_code = re.sub(
    r"_ACTIONS = json\.loads\(zlib\.decompress\(base64\.b85decode\('.*?'\)\)\.decode\('utf-8'\)\)",
    f"_ACTIONS = json.loads(zlib.decompress(base64.b85decode('{compressed}')).decode('utf-8'))",
    code,
    flags=re.DOTALL
)

with open('agents/v079_ai_after_hours_core.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
