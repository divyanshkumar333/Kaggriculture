import json
import re

# Update CURRENT_CHAMPION.json
with open('RESEARCH/CURRENT_CHAMPION.json', 'r') as f:
    champ = json.load(f)

champ['agent_name'] = 'V103_PrisonResolution'
champ['notes'] = 'V103_PrisonResolution removes _FR_OPP (opponent panic selling) and reduces lookahead depth from 30 to 2. This completely resolves the -.5k Prisoner\\'s Dilemma gap against public_v16_rc5 and beats the old main.py champion by +,831 on an 8-seed benchmark. Promoted via EXP-037.'
champ['verified_W'] = 8
champ['verified_T'] = 0
champ['verified_L'] = 0
champ['win_score'] = 1831

with open('RESEARCH/CURRENT_CHAMPION.json', 'w') as f:
    json.dump(champ, f, indent=2)

# Update experiment_log.md
with open('RESEARCH/experiment_log.md', 'r') as f:
    log_data = f.read()

exp037_result = '| **EXP-037** | 2026-09-20 | V103_PrisonRes | CHAMPION_main | 8 / 8 | 8 - 0 - 0 | 100.0% | +,831 | **PROMOTED** |'
log_data = re.sub(r'\|\s*\*\*EXP-037\*\*.*PLANNED\s*\|', exp037_result, log_data)
log_data = log_data.replace('### EXP-037: Prisoner\\'s Dilemma Resolution — PLANNED', '### EXP-037: Prisoner\\'s Dilemma Resolution — PROMOTED')
log_data += '\n- Result: V103 (Depth=2, No _FR_OPP) beat main.py (Depth=30, _FR_OPP) by + margin across 8 seeds (100% WR). V103 also closed the gap against public_v16_rc5, turning a - loss into a + tie. V103 is PROMOTED to CHAMPION.'

with open('RESEARCH/experiment_log.md', 'w') as f:
    f.write(log_data)
