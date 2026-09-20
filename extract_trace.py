import json, base64, zlib, re

with open('scratch/v057_original.py', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'base64\.b85decode\((b[\"''].*?[\"''])\)', content)
if match:
    b85_str = eval(match.group(1))
    json_str = zlib.decompress(base64.b85decode(b85_str)).decode('utf-8')
    with open('ai_after_hours_actions_hire5.json', 'w') as out:
        out.write(json_str)
    print('Successfully extracted trace to ai_after_hours_actions_hire5.json')
else:
    print('Failed to find payload in v057_original.py')
