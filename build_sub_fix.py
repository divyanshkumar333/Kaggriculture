import os
import tarfile

source_agent = 'agents/v057_generalized_spoiler.py'
payload = 'ai_after_hours_actions.json'

with open(source_agent, 'r', encoding='utf-8') as f:
    code = f.read()

safe_loader = '''
import os, json
_path = "/kaggle_simulations/agent/ai_after_hours_actions.json"
if not os.path.exists(_path):
    _path = "ai_after_hours_actions.json"
_ACTIONS = json.load(open(_path))
'''

code = code.replace(
    'import os, json\n_ACTIONS = json.load(open(os.path.join(os.path.dirname(__file__), \"..\", \"ai_after_hours_actions.json\")))',
    safe_loader
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(code)

with tarfile.open('submission.tar.gz', 'w:gz') as tar:
    tar.add('main.py')
    tar.add(payload)

print('Created fixed submission.tar.gz')
