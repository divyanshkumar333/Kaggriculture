import json, base64, zlib

with open('scratch/v057_original.py', encoding='utf-8') as f:
    lines = f.readlines()

code = ""
for line in lines:
    if line.startswith('def '):
        break
    code += line

local_env = {}
exec(code, globals(), local_env)

with open('ai_after_hours_actions_hire5.json', 'w') as out:
    json.dump(local_env['_ACTIONS'], out)

print('Successfully extracted trace to ai_after_hours_actions_hire5.json')
