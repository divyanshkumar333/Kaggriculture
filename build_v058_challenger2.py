import os
import tarfile

source_agent = 'agents/v058_generalized_spoiler.py'
payload = 'ai_after_hours_actions_hire5.json'

with open(source_agent, 'r', encoding='utf-8') as f:
    lines = f.readlines()

safe_loader = '''import os, json
_path = "/kaggle_simulations/agent/ai_after_hours_actions.json"
if not os.path.exists(_path):
    _path = "ai_after_hours_actions.json"
_ACTIONS = json.load(open(_path))
'''

code = ""
for i, line in enumerate(lines):
    if i == 17: # Line 18 (0-indexed)
        code += safe_loader
    elif i == 18:
        continue
    else:
        code += line

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(code)

with tarfile.open('submission_v058_challenger.tar.gz', 'w:gz') as tar:
    tar.add('main.py')
    tar.add(payload, arcname='ai_after_hours_actions.json')

print('Created submission_v058_challenger.tar.gz')
