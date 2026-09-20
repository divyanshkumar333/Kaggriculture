import os
import tarfile

source_agent = 'agents/v057_generalized_spoiler.py'
payload = 'ai_after_hours_actions.json'

with open(source_agent, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('\"..\", \"ai_after_hours_actions.json\"', '\"ai_after_hours_actions.json\"')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(code)

with tarfile.open('submission.tar.gz', 'w:gz') as tar:
    tar.add('main.py')
    tar.add(payload)

print('Created submission.tar.gz')
