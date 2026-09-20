import os
import tarfile

source_agent = 'agents/v058_generalized_spoiler.py'
payload = 'ai_after_hours_actions_hire5.json'

with open(source_agent, 'r', encoding='utf-8') as f:
    code = f.read()

# Make sure it loads the json correctly in Kaggle env
safe_loader = '''
import os, json
_path = "/kaggle_simulations/agent/ai_after_hours_actions.json"
if not os.path.exists(_path):
    _path = "ai_after_hours_actions.json"
_ACTIONS = json.load(open(_path))
'''
code = code.replace(
    'import os, json\n_path = \"/kaggle_simulations/agent/ai_after_hours_actions.json\"\nif not os.path.exists(_path):\n    _path = \"ai_after_hours_actions.json\"\nif not os.path.exists(_path):\n    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)) if \'__file__\' in globals() else \'.\', \'ai_after_hours_actions.json\')\n\n_ACTIONS = json.load(open(_path))',
    safe_loader
)

# wait, in build_sub_fix.py I already replaced it, so v058 might STILL have the old loader if I just copied it before build_sub_fix?
# Let's just use regex to replace whatever loader is there:
import re
code = re.sub(r'import os, sys, json.*_ACTIONS = json\.load\(open\(_path\)\)', safe_loader, code, flags=re.DOTALL)
code = re.sub(r'import os, json\n_ACTIONS = json\.load\(open\(.*?\)\)', safe_loader, code, flags=re.DOTALL)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(code)

with tarfile.open('submission_v058_challenger.tar.gz', 'w:gz') as tar:
    tar.add('main.py')
    # add the HIRE5 trace but name it ai_after_hours_actions.json inside the tar!
    tar.add(payload, arcname='ai_after_hours_actions.json')

print('Created submission_v058_challenger.tar.gz')
