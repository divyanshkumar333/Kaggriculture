import difflib

f1 = "agents/the_2945_farm.py"
f2 = "agents/v104_quote_priority.py"

with open(f1, 'r', encoding='utf-8') as file1, open(f2, 'r', encoding='utf-8') as file2:
    lines1 = file1.readlines()
    lines2 = file2.readlines()

diff = list(difflib.unified_diff(lines1, lines2, n=3))

print(f"Total lines in diff: {len(diff)}")
for line in diff[:30]:
    print(line, end='')
