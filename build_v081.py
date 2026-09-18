import json
import zlib
import base64
import re

actions = json.load(open('best_kaggle_trace.json'))
compressed = base64.b85encode(zlib.compress(json.dumps(actions).encode('utf-8'))).decode('ascii')

with open('agents/v057_generalized_spoiler.py', 'r', encoding='utf-8') as f:
    code = f.read()

# We need to find the b85 string inside the decode(b'...')
new_code = re.sub(
    r'base64\.b85decode\(b\'(.*?)\'\)',
    f"base64.b85decode(b'{compressed}')",
    code,
    flags=re.DOTALL
)

with open('agents/v081_kaggle_83k_trace.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
