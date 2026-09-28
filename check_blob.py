import sys, re
code = open('scratch/old_v057.py').read()
v057_blob = None
for line in code.splitlines():
    if len(line) > 1000 and 'c-rk' in line:
        v057_blob = line
        break
print('V057 blob length:', len(v057_blob) if v057_blob else 'NOT FOUND')

kaito = open('RESEARCH/external/kaito_v27_real/main.py').read()
kaito_blob = None
for line in kaito.splitlines():
    if len(line) > 1000 and 'c-rk' in line:
        kaito_blob = line
        break
print('Kaito blob length:', len(kaito_blob) if kaito_blob else 'NOT FOUND')

if v057_blob and kaito_blob:
    print('Are they identical?:', v057_blob == kaito_blob)
