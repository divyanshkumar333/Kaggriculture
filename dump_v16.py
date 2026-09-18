import base64
import json
import zlib
import sys
import importlib.util

spec = importlib.util.spec_from_file_location("v", "agents/v051_v16_lookahead30_final.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

a = v._ACTIONS
with open('v16_dump.json', 'w') as f:
    json.dump(a[:100], f, indent=2)
print("Dumped 100 turns to v16_dump.json")
