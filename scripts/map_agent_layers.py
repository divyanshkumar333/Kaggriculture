"""Map all the layered agent wrappers in the 2945 farm."""
import re

with open(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', encoding='utf-8') as f:
    content = f.read()

# Count all 'del agent' and 'def agent' occurrences
del_agents = [content.count('\n', 0, i) + 1 for i in range(len(content)-10) if content[i:i+10] == 'del agent\n']
def_agents = [content.count('\n', 0, i) + 1 for i in range(len(content)-9) if content[i:i+9] == 'def agent']

print(f'"del agent" count: {len(del_agents)}')
print(f'"def agent" count: {len(def_agents)}')

print('\nLayer stack (def agent positions):')
for linenum in def_agents:
    lines = content.split('\n')
    ctx = lines[linenum-1][:80] if linenum <= len(lines) else '?'
    # Find the preceding comment block (look up 10 lines for EXP or layer name)
    label = ''
    for i in range(linenum-2, max(linenum-15, 0), -1):
        if i < len(lines) and ('EXP' in lines[i] or '# ' in lines[i]):
            label = lines[i].strip()[:80]
            break
    print(f'  Line {linenum}: {label}')

# Find all _RXXXX_*_PARENT assignments
parent_assigns = re.findall(r'(_[A-Z]\d+_\w+PARENT)\s*=\s*agent', content)
print(f'\nParent aliases ({len(parent_assigns)}):')
for p in parent_assigns:
    idx = content.find(p + ' = agent')
    linenum = content.count('\n', 0, idx) + 1
    print(f'  Line {linenum}: {p} = agent')
