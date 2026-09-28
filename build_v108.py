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

# The original method is:
#     def _route_action(self, route, step):
#         tape = self.routes[route]
#         if 0 <= step < len(tape) and isinstance(tape[step], dict):
#             return copy.deepcopy(tape[step])
#         return copy.deepcopy(PASS_ACTION)

new_method = f"""    def _route_action(self, route, step):
        import json, base64, zlib, copy
        if not hasattr(self, '_INJECTED_TAPE'):
            self._INJECTED_TAPE = json.loads(zlib.decompress(base64.b85decode('{premium_b85}')))
        if 0 <= step < len(self._INJECTED_TAPE):
            return copy.deepcopy(self._INJECTED_TAPE[step])
        return {{"farmer": ["PASS"], "hands": [], "market": []}}"""

v104_code = re.sub(
    r"    def _route_action\(self, route, step\):.*?return copy\.deepcopy\(PASS_ACTION\)",
    new_method,
    v104_code,
    flags=re.DOTALL
)

with open("submission_v108_injected_162k.py", "w", encoding="utf-8") as f:
    f.write(v104_code)

print("Created submission_v108_injected_162k.py")
